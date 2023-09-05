from typing import List, Dict, Any, Union, Optional
import enum
from pydantic import AnyUrl, BaseModel, validator, EmailStr, IPvAnyAddress
from datetime import datetime
from datetime import time
from sqlalchemy import (
    Column,
    BigInteger,
    Column,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Boolean,
    String,
    Table,
    Text,
    event,
    and_,
    cast,
)
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

Base = declarative_base()


class CommonMethods:
    def is_pydantic(self, obj: object):
        """Checks whether an object is pydantic."""
        return type(obj).__class__.__name__ == "ModelMetaclass"

    def pydantic_to_sqlalchemy_model(self, schema):
        parsed_schema = dict(schema)
        for key, value in parsed_schema.items():
            try:
                if (
                    isinstance(value, list)
                    and len(value)
                    and self.is_pydantic(value[0])
                ):
                    parsed_schema[key] = [
                        item.Meta.orm_model(**self.pydantic_to_sqlalchemy_model(item))
                        for item in value
                    ]
                elif self.is_pydantic(value):
                    parsed_schema[key] = value.Meta.orm_model(
                        **self.pydantic_to_sqlalchemy_model(value)
                    )
            except AttributeError:
                raise AttributeError(
                    f"Found nested Pydantic model in {schema.__class__} but Meta.orm_model was not specified."
                )
        return parsed_schema

    @property
    def as_dict(self):
        return self.dict()


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone_number = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum("owner", "admin", "user", name="role"), default="user")
    lancaster_login = Column(String(255))
    lancaster_password = Column(String(255))
    otp_email = Column(String(255))
    otp_password = Column(String(255))

    # Fields from the CustomerPolicyTable
    date_start = Column(Date)
    date_end = Column(Date)
    max_puppies = Column(Integer)
    max_runs = Column(Integer)

    @hybrid_property
    def is_customer_policy_active(self):
        if self.date_start is None or self.date_end is None:
            return False
        date_start = datetime.combine(self.date_start, time.min)
        date_end = datetime.combine(self.date_end, time.max)

        # Check if the current datetime is within `date_start` and `date_end`
        return date_start <= datetime.utcnow() <= date_end

    logs = relationship("LogTable", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    scraping_tasks = relationship("ScrapingTaskTable", backref="task_user", cascade="all, delete-orphan")

    @is_customer_policy_active.expression
    def is_customer_policy_active(cls):
        now = func.now()
        return and_(cls.date_start <= now, now <= cls.date_end)

    proxies = relationship(
        "ProxyTable", backref=backref("proxy_user", lazy="joined"), lazy="dynamic"
    )
    time_created = Column(DateTime, default=datetime.utcnow)
    time_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # def delete(self, session):
    #     """Delete the user and commit the transaction."""
    #
    #     # We are assuming that ProxyTable.user_id can be null.
    #     # If this is not the case, you may need to delete the proxies or handle them differently.
    #     for proxy in self.proxies:
    #         proxy.user_id = None
    #
    #     session.delete(self)
    async def delete(self, db):
        self.proxies.user_id = None
        db.delete(self)
        db.commit()


class ProxyTable(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True, index=True)
    proxy = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserTable", back_populates="proxies", overlaps="proxy_user")

    is_active = Column(Boolean, default=True)
    time_created = Column(DateTime, default=datetime.utcnow)
    time_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # def delete(self, db):
    #     self.scraping_task.proxy = None
    #     db.delete(self)
    #     db.commit()


class TaskStatusEnum(enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    WAITING = "waiting"


class TaskResultEnum(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class ScrapingTaskTable(Base):
    __tablename__ = "scraping_tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship(
        "UserTable", back_populates="scraping_tasks", overlaps="task_user"
    )
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    # foreign key to the proxy table
    proxy_id = Column(Integer, ForeignKey("proxies.id", ondelete="SET NULL"))
    proxy = relationship("ProxyTable", backref="scraping_tasks")
    current_status = Column(String(255), default=TaskStatusEnum.STOPPED.value)
    task_result = Column(String(255), default="pending")
    task_result_detail = Column(Text)
    time_created = Column(DateTime, default=datetime.utcnow)
    time_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogTable(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("UserTable", back_populates="logs")
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String, nullable=False, default="INFO")
    message = Column(String)


class LogBase(BaseModel):
    id: int
    timestamp: Optional[datetime]
    level: Optional[LogLevelEnum]
    message: Optional[str]


class LogResponse(LogBase):
    class Config:
        orm_mode = True


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    user = "user"


class User(BaseModel, CommonMethods):
    id: Optional[int]
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    hashed_password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role: Role = Role.user
    time_created: Optional[datetime]
    time_updated: Optional[datetime]

    class Config:
        orm_mode = True


class CreateAccountRequest(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    password: str


class CreateAccountResponse(BaseModel):
    token: str
    token_type: str


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class TokenData(BaseModel):
    user_id: str
    role: str = "user"


class UserCredentialsRequest(BaseModel):
    lancaster_email: EmailStr
    lancaster_password: str
    gmail_username: str
    gmail_password: str


class UserCredentialsResponse(BaseModel):
    lancaster_email: Optional[EmailStr]
    lancaster_password: Optional[str]
    gmail_username: Optional[str]
    gmail_password: Optional[str]


class GeneralResponse(BaseModel):
    result: str
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class UserAccountInfo(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    password: str

class CreateCustomerRequest(BaseModel):
    date_start: Optional[Any]
    date_end: Optional[Any]
    max_puppies: Optional[Any]
    max_runs: Optional[Any]
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    role: Optional[str]

class CustomerResponse(BaseModel):
    date_start: Optional[Union[Any, None]]
    date_end: Optional[Union[Any, None]]
    max_puppies: Optional[Union[int, None]]
    max_runs: Optional[Union[int, None]]
    status: Optional[bool]
    email: str
    password: Optional[Union[str, None]]
    first_name: Optional[Union[str, None]]
    last_name: Optional[Union[str, None]]
    phone_number: Optional[Union[str, None]]
    role: Optional[str]
    user_id: int
    current_status: Optional[str]
    task_today_runs: Optional[int]
    task_result: Optional[str]
    task_result_detail: Optional[str]
    task_date_end: Optional[Union[Any, None]]

    @validator("date_start", "date_end", pre=True)
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @validator("task_date_end", pre=True)
    def parse_date2(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value


class UserScraperCredentials(BaseModel):
    lancaster_email: EmailStr
    lancaster_password: str
    gmail_username: str
    gmail_password: str
    user_id: int
    max_puppies: Union[int, None]
    proxy: Union[str, None]
