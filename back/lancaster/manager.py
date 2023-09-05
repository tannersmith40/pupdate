from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from back.lancaster.config import db_config
import asyncpg


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBManager(metaclass=Singleton):
    def __init__(self,  db_url=None, async_db_url=None):
        self.__async_engine = create_async_engine(
            async_db_url,
            echo=True,
        )
        self.__engine = create_engine(
            db_url,
            echo=False,
        )


        self.async_session = AsyncSession(self.__async_engine, expire_on_commit=False)
        self.session = sessionmaker(bind=self.__engine)

    def close_engine(self):
        """
        Close the SQLAlchemy Engine associated with this manager.
        """
        self.__engine.dispose()

    def close_async_engine(self):
        """
        Close the SQLAlchemy async Engine associated with this manager.
        """
        self.__async_engine.dispose()

    def get_session(self):
        return self.session()
    @property
    def async_engine(self):
        return self.__async_engine

    @property
    def engine(self):
        return self.__engine


db_manager = DBManager(async_db_url=db_config.dsn_async,db_url=db_config.dsn_async)
get_db = lambda: db_manager.engine
get_async_session = lambda: AsyncSession(db_manager.async_engine, expire_on_commit=False)

# class DBManager:
#     def __init__(self, db_url=None, async_db_url=None):
#         self.__async_engine = create_async_engine(
#             async_db_url,
#             echo=False,
#         )
#         self.__engine = create_engine(
#             db_url,
#             echo=False,
#         )
#         self.session_factory = sessionmaker(bind=self.__engine)
#         self.async_session_factory = AsyncSession(self.__async_engine, expire_on_commit=False)
#
#     async def get_async_session(self):
#         """
#         Returns a new AsyncSession that should be used in a context manager to ensure proper cleanup.
#         """
#         return self.async_session_factory()
#
#     def get_session(self):
#         """
#         Returns a new Session that should be used in a context manager to ensure proper cleanup.
#         """
#         return self.session_factory()
#
#     @property
#     def async_engine(self):
#         return self.__async_engine
#
#     @property
#     def engine(self):
#         return self.__engine
#
#     def get_db(self):
#         """
#         Returns the SQLAlchemy Engine associated with this manager.
#         """
#         return self.__engine
#
#     def get_async_db(self):
#         """
#         Returns the SQLAlchemy async Engine associated with this manager.
#         """
#         return self.__async_engine
#
#
# db_manager = DBManager(async_db_url=db_config.dsn_async,db_url=db_config.dsn_async)
# get_async_session = lambda: AsyncSession(db_manager.async_engine, expire_on_commit=False)

