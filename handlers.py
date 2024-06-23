from pyrogram import Client, filters
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
import datetime


# Функция для обработки входящих сообщений

async def handle_message(client: Client, message):
    session: AsyncSession = client.session  # Получение сессии базы данных из клиента
    # Поиск пользователя в базе данных по user_id
    user = await session.execute(select(User).filter(User.user_id == message.from_user.id))
    user = user.scalar()  # Получение первого результата запроса

    if not user:  # Если пользователь не найден в базе данных
        user = User(user_id=message.from_user.id,
                    first_name=message.from_user.first_name)  # Создание нового пользователя
        session.add(user)  # Добавление пользователя в сессию
        await session.commit()  # Сохранение изменений в базе данных
        await message.reply("msg_1")  # Отправка первого сообщения пользователю
        user.msg_1_sent = True  # Установка флага отправки первого сообщения
        user.last_message_time = datetime.datetime.utcnow()  # Обновление времени последнего сообщения
        await session.commit()  # Сохранение изменений в базе данных
    elif "прекрасно" in message.text.lower() or "ожидать" in message.text.lower():  # Проверка наличия триггерных слов в сообщении
        user.status = "finished"  # Обновление статуса пользователя на "finished"
        user.status_update_at = datetime.datetime.utcnow()  # Обновление времени изменения статуса
        await session.commit()  # Сохранение изменений в базе данных
        await message.reply("Воронка прекращена. Спасибо за участие!")  # Отправка сообщения о завершении воронки
