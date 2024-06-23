from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime

Base = declarative_base()  # Создание базового класса для декларативных моделей SQLAlchemy


# Определение модели User, представляющей таблицу users в базе данных
class User(Base):
    __tablename__ = 'users'  # Имя таблицы в базе данных
    id = Column(Integer, primary_key=True, index=True)  # Первичный ключ, автоинкрементный идентификатор
    user_id = Column(Integer, unique=True, index=True)  # Уникальный идентификатор пользователя Telegram
    first_name = Column(String)  # Имя пользователя
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Время регистрации пользователя в воронку
    status = Column(String, default="alive")  # Статус пользователя (alive, dead, finished)
    status_update_at = Column(DateTime, default=datetime.datetime.utcnow)  # Время последнего обновления статуса
    last_message_time = Column(DateTime, default=datetime.datetime.utcnow)  # Время последнего отправленного сообщения
    msg_1_sent = Column(Boolean, default=False)  # Флаг отправки первого сообщения
    msg_2_sent = Column(Boolean, default=False)  # Флаг отправки второго сообщения
    msg_3_sent = Column(Boolean, default=False)  # Флаг отправки третьего сообщения


# URL для подключения к базе данных
DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase"

# Создание асинхронного двигателя для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание асинхронной сессии для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# Функция инициализации базы данных, создающая все таблицы
async def init_db():
    async with engine.begin() as conn:  # Открытие асинхронного соединения с базой данных
        await conn.run_sync(Base.metadata.create_all)  # Создание всех таблиц, определенных в моделях
