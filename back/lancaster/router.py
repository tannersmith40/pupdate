from typing import List, Dict, Any, Union, Optional, Annotated
from fastapi import BackgroundTasks, APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from back.lancaster.manager import db_manager
from back.lancaster.models import (
    User,
    CreateAccountRequest,
    UserCredentialsRequest,
    GeneralResponse,
    Token,
    UserCredentialsResponse,
    UserAccountInfo,
    CustomerResponse,
    LogBase,
CreateCustomerRequest
)
from back.lancaster.service import LancasterService


lancaster_router = APIRouter(
    prefix="/api",
    tags=["Lancaster"],
    include_in_schema=True,
)


@lancaster_router.post(
    path="/token",
    summary="Login",
    response_model=Token,
    include_in_schema=True,
)
async def login(payload: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.login(payload)
    return task_data


@lancaster_router.post(
    path="/create-account",
    summary="Create user account",
    response_model=Token,
    include_in_schema=True,
)
async def create_account(payload: CreateAccountRequest) -> Token:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.create_account(payload)
    return task_data


@lancaster_router.post(
    path="/user_credentials",
    summary="Set user credentials",
    response_model=GeneralResponse,
    include_in_schema=True,
)
async def set_user_credentials(
    payload: UserCredentialsRequest,
    current_user: Annotated[User, Depends(LancasterService.get_current_active_user)],
) -> UserCredentialsResponse:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.set_user_credentials(payload, current_user)
    return task_data


@lancaster_router.get(
    path="/user_credentials",
    summary="Get user credentials",
    response_model=UserCredentialsResponse,
    include_in_schema=True,
)
async def get_user_credentials(
    current_user: Annotated[User, Depends(LancasterService.get_current_active_user)]
) -> UserCredentialsResponse:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.get_user_credentials(current_user)
    return task_data


@lancaster_router.get(
    path="/account-info",
    summary="Get account info",
    response_model=UserAccountInfo,
    include_in_schema=True,
)
async def get_account_info(
    current_user: Annotated[User, Depends(LancasterService.get_current_active_user)]
) -> UserAccountInfo:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.get_account_info(current_user)
    return task_data


@lancaster_router.post(
    path="/account-info",
    summary="Update account info",
    response_model=GeneralResponse,
    include_in_schema=True,
)
async def update_account_info(
    payload: UserAccountInfo,
    current_user: Annotated[User, Depends(LancasterService.get_current_active_user)],
) -> GeneralResponse:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.update_account_info(payload, current_user)
    return task_data


@lancaster_router.get(
    path="/customer",
    summary="Get all customers",
    response_model=List[CustomerResponse],
    include_in_schema=True,
)
async def get_customer(
    current_user: Annotated[User, Depends(LancasterService.check_user_role)]
) -> List[CustomerResponse]:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.get_customers(current_user)
    return task_data


@lancaster_router.put(
    path="/customer",
    summary="Update customer",
    response_model=CustomerResponse,
    include_in_schema=True,
)
async def update_customer(
    payload: CustomerResponse,
    current_user: Annotated[User, Depends(LancasterService.check_user_role)],
) -> CustomerResponse:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.update_customer(payload, current_user)
    return task_data

# create_customer
@lancaster_router.post(
    path="/customer",
    summary="Create customer",
    response_model=CustomerResponse,
    include_in_schema=True,
)
async def create_customer(
    payload: CreateCustomerRequest,
    current_user: Annotated[User, Depends(LancasterService.check_user_role)],
) -> CustomerResponse:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.create_customer(payload, current_user)
    return task_data


# delete customer
@lancaster_router.delete(
    path="/customer/{user_id}",
    summary="Delete customer",
    response_model=GeneralResponse,
    include_in_schema=True,
)
async def delete_customer(
    user_id: int,
    current_user: Annotated[User, Depends(LancasterService.check_user_role)],
) -> GeneralResponse:

    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.delete_customer(user_id, current_user)
    return task_data


@lancaster_router.get(
    path="/logs",
    summary="Get all logs",
    response_model=List[LogBase],
    include_in_schema=True,
)
async def get_logs(
    current_user: Annotated[User, Depends(LancasterService.get_current_active_user)]
) -> List[LogBase]:
    async with db_manager.async_session as session:
        service = LancasterService(session)
        task_data = await service.get_logs(current_user)
    return task_data
