import asyncio
from pyrogram import Client, errors, filters
from config import BOT_TOKEN, API_ID, API_HASH
from handlers import handle_message
from models import init_db, SessionLocal, User
from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select

# Создание клиента Pyrogram с заданными API ID, API Hash и токеном бота

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# Обработчик входящих сообщений
@app.on_message(filters.command)
async def message_handler(client, message):
    async with SessionLocal() as session:  # Создание новой сессии базы данных
        client.session = session  # Присвоение сессии клиенту
        await handle_message(client, message)  # Вызов функции для обработки сообщения


# Функция для отправки запланированных сообщений
async def send_scheduled_messages():
    while True:  # Бесконечный цикл
        async with SessionLocal() as session:  # Создание новой сессии базы данных
            async with session.begin():  # Начало транзакции
                # Выбор всех пользователей со статусом "alive"
                users = await session.execute(select(User).filter(User.status == "alive"))
                users = users.scalars().all()  # Получение всех пользователей
                now = datetime.now(timezone.utc)  # Получение текущего времени в UTC

                for user in users:  # Проход по всем пользователям
                    try:
                        # Проверка времени для отправки второго сообщения
                        if not user.msg_2_sent and now > user.last_message_time + timedelta(minutes=6):
                            await app.send_message(user.user_id, "msg_2")  # Отправка второго сообщения
                            user.msg_2_sent = True  # Установка флага отправки второго сообщения
                            user.last_message_time = now  # Обновление времени последнего сообщения
                            await session.commit()  # Сохранение изменений в базе данных
                        # Проверка времени для отправки третьего сообщения
                        elif not user.msg_3_sent and now > user.last_message_time + timedelta(days=1, hours=2):
                            await app.send_message(user.user_id, "msg_3")  # Отправка третьего сообщения
                            user.msg_3_sent = True  # Установка флага отправки третьего сообщения
                            user.status = "finished"  # Обновление статуса пользователя на "finished"
                            user.status_update_at = now  # Обновление времени изменения статуса
                            await session.commit()  # Сохранение изменений в базе данных
                    except (errors.UserIsBlocked, errors.PeerIdInvalid,
                            errors.UserDeactivated):  # Обработка ошибок блокировки пользователя или деактивации аккаунта
                        user.status = "dead"  # Обновление статуса пользователя на "dead"
                        user.status_update_at = now  # Обновление времени изменения статуса
                        await session.commit()  # Сохранение изменений в базе данных

        await asyncio.sleep(60)  # Ожидание 60 секунд перед следующим циклом


# Основная функция
async def main():
    await init_db()  # Инициализация базы данных
    await app.start()  # Запуск клиента Pyrogram
    await send_scheduled_messages()  # Запуск функции отправки запланированных сообщений


if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
