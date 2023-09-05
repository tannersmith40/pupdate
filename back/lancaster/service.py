from typing import List, Optional, Dict, Annotated
import traceback
import pytz
from pydantic.typing import NoneType
from back.lancaster.models import (
    User,
    CreateAccountRequest,
    UserTable,
    CreateAccountResponse,
    LoginRequest,
    TokenData,
    UserCredentialsRequest,
    UserCredentialsResponse,
    Token,
    GeneralResponse,
    UserAccountInfo,
    CustomerResponse,
    LogBase,
    LogTable,
    LogResponse,
    ScrapingTaskTable,
    CreateCustomerRequest,
)
from back.lancaster.manager import db_manager, get_async_session
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc, func
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 60 * 24 * 7  # 7 days

DB = None


class LancasterService:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or db_manager.db
        global DB
        DB = self.session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def api_token_auth(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise self.credentials_exception
            token_data = TokenData(user_id=user_id)
        except JWTError:
            raise self.credentials_exception
        return token_data

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], conn=Depends(get_async_session)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = int(payload.get("sub"))
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(user_id=user_id)
        except JWTError as e:
            raise credentials_exception
        async with conn.begin():
            db_user = await conn.execute(
                select(UserTable).where(UserTable.id == user_id)
            )
            user = db_user.scalar_one_or_none()
        await conn.close()
        if db_user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(
        current_user: Annotated[UserTable, Depends(get_current_user)]
    ):
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    async def login(self, payload: LoginRequest) -> Token:
        async with self.session.begin():
            db_user = await self.session.execute(
                select(UserTable).where(UserTable.email == payload.username)
            )
            user = db_user.scalar_one_or_none()
            if user is None:
                raise HTTPException(status_code=400, detail="Email not registered")

            if not self.verify_password(payload.password, user.hashed_password):
                raise HTTPException(status_code=400, detail="Incorrect password")
            if not user.is_active:
                raise HTTPException(status_code=400, detail="Inactive user")
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
            return Token(
                access_token=self.create_access_token(
                    data={"sub": str(user.id)},
                ),
                token_type="bearer",
                role=user.role,
            )

    async def check_user_role(
        current_user: UserTable = Depends(get_current_active_user),
    ):
        if current_user.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    async def create_account(self, payload: CreateAccountRequest) -> Token:
        async with self.session.begin():
            try:
                db_user = await self.session.execute(
                    select(UserTable).where(UserTable.email == payload.email)
                )
                if db_user.scalar_one_or_none() is not None:
                    raise HTTPException(
                        status_code=400, detail="Email already registered"
                    )
                hashed_password = self.get_password_hash(payload.password)
                # create user in your database
                try:
                    user = UserTable(
                        email=payload.email,
                        first_name=payload.first_name,
                        last_name=payload.last_name,
                        phone_number=payload.phone_number,
                        hashed_password=hashed_password,
                        is_active=True,
                    )
                    self.session.add(user)
                    await self.session.commit()
                except Exception as e:
                    i = 1
                user_id = user.id
                return Token(
                    access_token=self.create_access_token(
                        data={"sub": str(user_id)},
                    ),
                    token_type="bearer",
                    role="user",
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                import traceback

                print(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail="An error occurred while creating your account.",
                )
            try:
                user = User(
                    email=payload.email,
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    password=payload.password,
                    is_active=True,
                )
                self.session.add(user)
                await self.session.commit()
                return user
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def set_user_credentials(
        self,
        payload: UserCredentialsRequest,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> GeneralResponse:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(UserTable).where(UserTable.id == current_user.id)
                )
                current_user = result.scalars().first()
                current_user.lancaster_login = payload.lancaster_email
                current_user.lancaster_password = payload.lancaster_password
                current_user.otp_email = payload.gmail_username
                current_user.otp_password = payload.gmail_password
                self.session.add(current_user)
                await self.session.commit()
                return GeneralResponse(result="success", detail="Credentials updated")
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        ...

    async def get_user_credentials(
        self, current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> UserCredentialsResponse:
        async with self.session.begin():
            return UserCredentialsResponse(
                lancaster_email=current_user.lancaster_login,
                lancaster_password=current_user.lancaster_password,
                gmail_username=current_user.otp_email,
                gmail_password=current_user.otp_password,
            )

    async def get_account_info(
        self, current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> UserAccountInfo:
        async with self.session.begin():
            return UserAccountInfo(
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                phone_number=current_user.phone_number,
                password="****",
            )

    async def update_account_info(
        self,
        payload: UserAccountInfo,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> GeneralResponse:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(UserTable).where(UserTable.id == current_user.id)
                )
                current_user = result.scalars().first()
                current_user.first_name = payload.first_name
                current_user.last_name = payload.last_name
                current_user.phone_number = payload.phone_number
                current_user.email = payload.email
                # if payload.password is not None:
                #     current_user.hashed_password = self.get_password_hash(
                #         payload.password
                #     )
                self.session.add(current_user)
                await self.session.commit()
                return GeneralResponse(result="success", detail="Account updated")
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def get_customer(
        self,
        current_user: Annotated[User, Depends(check_user_role)],
    ) -> CustomerResponse:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(UserTable).where(UserTable.id == current_user.id)
                )
                user = result.scalars().first()
                result = await self.session.execute(
                    select(ScrapingTaskTable)
                    .where(ScrapingTaskTable.user_id == user.id)
                    .order_by(
                        desc(
                            func.coalesce(
                                ScrapingTaskTable.date_end, ScrapingTaskTable.date_start
                            )
                        )
                    )
                    .limit(1)
                )
                last_task = result.scalars().first()
                return CustomerResponse(
                    date_start=user.date_start,
                    date_end=user.date_end,
                    max_puppies=user.max_puppies,
                    max_runs=user.max_runs,
                    is_active=user.is_customer_policy_active,
                    email=user.email,
                    password="",
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    current_status=last_task.status if last_task is not None else None,
                    task_result=last_task.result if last_task is not None else None,
                    task_date_end=last_task.date_end
                    if last_task.date_end is not None
                    else last_task.date_start,
                    task_result_detail=last_task.result_detail
                    if last_task is not None
                    else None,
                )

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    async def get_customers(
        self,
        current_user: Annotated[User, Depends(check_user_role)],
    ) -> List[CustomerResponse]:
        async with self.session.begin():
            try:
                result = await self.session.execute(select(UserTable))
                users = result.scalars().all()
                customer_responses = []
                for user in users:
                    result = await self.session.execute(
                        select(ScrapingTaskTable)
                        .where(ScrapingTaskTable.user_id == user.id)
                        .order_by(
                            desc(
                                func.coalesce(
                                    ScrapingTaskTable.date_end,
                                    ScrapingTaskTable.date_start,
                                )
                            )
                        )
                        .limit(1)
                    )
                    last_task = result.scalars().first()
                    if last_task is not None:
                        task_date_end = (
                            last_task.date_end
                            if last_task.date_end is not None
                            else last_task.date_start
                        )
                    else:
                        task_date_end = None
                    tasks_today = (
                        (
                            await self.session.execute(
                                select(ScrapingTaskTable)
                                .where(ScrapingTaskTable.user_id == user.id)
                                .where(
                                    ScrapingTaskTable.date_start
                                    >= datetime.utcnow().date()
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )
                    if tasks_today:
                        today_runs = len(tasks_today)
                    else:
                        today_runs = None
                    customer_responses.append(
                        CustomerResponse(
                            date_start=user.date_start,
                            date_end=user.date_end,
                            max_puppies=user.max_puppies,
                            max_runs=user.max_runs,
                            status=user.is_customer_policy_active,
                            email=user.email,
                            # password="",
                            first_name=user.first_name,
                            last_name=user.last_name,
                            phone_number=user.phone_number,
                            role=user.role,
                            user_id=user.id,
                            current_status=last_task.current_status
                            if last_task is not None
                            else None,
                            task_result=last_task.task_result
                            if last_task is not None
                            else None,
                            task_today_runs=today_runs,
                            task_date_end=task_date_end,
                            task_result_detail=last_task.task_result_detail
                            if last_task is not None
                            else None,
                        )
                    )
                return customer_responses
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    async def update_customer(
        self,
        payload: CustomerResponse,
        current_user: Annotated[User, Depends(check_user_role)],
    ) -> CustomerResponse:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(UserTable).where(UserTable.id == payload.user_id)
                )
                user = result.scalars().first()
                user.first_name = payload.first_name
                user.last_name = payload.last_name
                user.phone_number = payload.phone_number
                user.email = payload.email
                user.role = payload.role

                user.date_start = payload.date_start
                user.date_end = payload.date_end
                user.max_puppies = payload.max_puppies
                user.max_runs = payload.max_runs
                if payload.password is not None and payload.password != "":
                    user.hashed_password = self.get_password_hash(payload.password)
                self.session.add(user)
                await self.session.commit()
                return CustomerResponse(
                    date_start=user.date_start,
                    date_end=user.date_end,
                    max_puppies=user.max_puppies,
                    max_runs=user.max_runs,
                    email=user.email,
                    status=user.is_customer_policy_active,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    role=user.role,
                    user_id=user.id,
                )
            except Exception as e:
                import traceback

                print(traceback.format_exc())
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    # create customer
    async def create_customer(
        self,
        payload: CreateCustomerRequest,
        current_user: Annotated[User, Depends(check_user_role)],
    ) -> CustomerResponse:
        async with self.session.begin():
            db_user = await self.session.execute(
                select(UserTable).where(UserTable.email == payload.email)
            )
            if db_user.scalar_one_or_none() is not None:
                raise HTTPException(status_code=400, detail="Email already registered")
            hashed_password = self.get_password_hash(payload.password)
            # create user in your database
            try:
                user = UserTable(
                    email=payload.email,
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    phone_number=payload.phone_number,
                    hashed_password=hashed_password,
                    is_active=True,
                    # role=payload.role,
                    # date_start=payload.date_start,
                    # date_end=payload.date_end,
                    max_puppies=int(payload.max_puppies)
                    if payload.max_puppies
                    else None,
                    max_runs=int(payload.max_runs) if payload.max_runs else None,
                )
                self.session.add(user)
                await self.session.commit()
            except Exception as e:
                print(traceback.format_exc())
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))
            return CustomerResponse(
                date_start=user.date_start,
                date_end=user.date_end,
                max_puppies=user.max_puppies,
                max_runs=user.max_runs,
                email=user.email,
                status=user.is_customer_policy_active,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                role=user.role,
                user_id=user.id,
            )

    # delete customer form user table with id=user_id
    async def delete_customer(
        self,
        user_id: int,
        current_user: Annotated[User, Depends(check_user_role)],
    ) -> GeneralResponse:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(UserTable).where(UserTable.id == user_id)
                )
                user = result.scalars().first()
                if user:
                    # user.delete(self.session)
                    await self.session.delete(user)
                    await self.session.commit()
                else:
                    raise HTTPException(status_code=404, detail="User not found")
                return GeneralResponse(result="success", detail="Customer deleted")
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    # Return all logs records from LogTable with given status (default status="INFO" for current user
    async def get_logs(
        self,
        current_user: UserTable = Depends(get_current_active_user),
        status: str = "INFO",
    ) -> List[LogResponse]:
        async with self.session.begin():
            try:
                result = await self.session.execute(
                    select(LogTable)
                    .where(LogTable.user_id == current_user.id)
                    .where(LogTable.level == status)
                    .where(
                        LogTable.timestamp >= datetime.utcnow() - timedelta(hours=48)
                    )
                    .order_by(desc(LogTable.timestamp))
                )
                logs = result.scalars().all()
                log_responses = []
                for log in logs:
                    log_responses.append(
                        LogResponse(
                            id=log.id,
                            level=log.level,
                            timestamp=pytz.utc.localize(log.timestamp),
                            message=log.message,
                        )
                    )
                return log_responses
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
