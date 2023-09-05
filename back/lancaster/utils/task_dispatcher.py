from typing import List, Dict, Any, Union, Optional
import asyncio
from datetime import datetime
from sqlalchemy import delete, select, update, desc, asc, or_, and_
from back.lancaster.manager import get_async_session
from back.lancaster.models import (
    ProxyTable,
    UserTable,
    ScrapingTaskTable,
    TaskStatusEnum,
    UserScraperCredentials,
)
from scraper.celery_worker import scrape_task
from back.lancaster.config import Config


# Get users from UserTable where is_customer_policy_active is True.
# For each user, check in ScrapingTaskTable  that now:
# 1. No task belonging to the user is running, field current_status
# 2. At least 90 minutes have passed since the end of the last task, date_end
# If both conditions are met, create a new task in ScrapingTaskTable
# start a new celery task scrape_task, pass the task_id and user credentials to the task
async def run_dispatcher():
    session = get_async_session()
    while True:
        print("Running task dispatcher")
        if True:
            async with session.begin():

                users = await session.execute(
                    select(UserTable).where(UserTable.is_customer_policy_active == True)
                )
                for user in users.scalars():
                    await session.refresh(user)
                    # Check if there is a task running for the user
                    task = (
                        await session.execute(
                            select(ScrapingTaskTable)
                            .where(ScrapingTaskTable.user_id == user.id)
                            .where(
                                or_(
                                    ScrapingTaskTable.current_status
                                    == TaskStatusEnum.RUNNING.value,
                                    ScrapingTaskTable.current_status
                                    == TaskStatusEnum.WAITING.value,
                                )
                            )
                        )
                    ).scalar_one_or_none()
                    if task:
                        continue

                    # check number of user tasks with date_start=today not more than max_runs.
                    if user.max_runs and user.max_runs > 0:
                        today = datetime.utcnow().date()
                        tasks_today = (
                            (
                                await session.execute(
                                    select(ScrapingTaskTable)
                                    .where(ScrapingTaskTable.user_id == user.id)
                                    .where(ScrapingTaskTable.date_start >= today)
                                )
                            )
                            .scalars()
                            .all()
                        )
                        if len(tasks_today) >= user.max_runs:
                            continue

                    # Check if the last task ended more than 90 minutes ago
                    task = (
                        (
                            await session.execute(
                                select(ScrapingTaskTable)
                                .where(
                                    and_(
                                        ScrapingTaskTable.user_id == user.id,
                                        ScrapingTaskTable.date_end != None,
                                        ScrapingTaskTable.current_status
                                        != TaskStatusEnum.RUNNING.value,
                                        ScrapingTaskTable.current_status
                                        != TaskStatusEnum.WAITING.value,
                                    ),
                                )
                                .order_by(ScrapingTaskTable.date_end.desc())
                            )
                        )
                        .scalars()
                        .first()
                    )

                    if task:
                        # print(
                        #     f"{datetime.now()} {task.date_end} {(datetime.now() - task.date_end).total_seconds()}"
                        # )
                        if (datetime.now() - task.date_end).total_seconds() < 5400:
                            continue
                    # Select a proxy for the task
                    # Check if there is a proxy assigned to the user
                    # if not then select a proxy from ProxyTable and bind it to the user
                    proxy = (
                        await session.execute(
                            select(ProxyTable)
                            .where(ProxyTable.user_id == user.id)
                            .where(ProxyTable.is_active == True)
                        )
                    ).scalar_one_or_none()
                    if not proxy:
                        proxy = (
                            await session.execute(
                                select(ProxyTable)
                                .where(ProxyTable.user_id == None)
                                .where(ProxyTable.is_active == True)
                            )
                        ).scalars().first()
                        if proxy:
                            proxy.user_id = user.id
                            await session.flush()
                            await session.refresh(proxy)
                        else:
                            # No proxy available
                            print(f"No proxy available for user {user.id}")
                            continue

                    # Create a new task
                    task = ScrapingTaskTable(
                        user_id=user.id,
                        proxy_id=proxy.id,
                        current_status=TaskStatusEnum.WAITING.value,
                    )
                    session.add(task)

                    await session.flush()
                    await session.refresh(task)
                    # Start a new celery task
                    result = scrape_task.delay(
                        user_credentials=UserScraperCredentials(
                            lancaster_email=user.lancaster_login,
                            lancaster_password=user.lancaster_password,
                            gmail_username=user.otp_email,
                            gmail_password=user.otp_password,
                            user_id=user.id,
                            max_puppies=user.max_puppies,
                            proxy=proxy.proxy,
                        ).dict(),
                        task_id=task.id,
                    )
                    print(f"Started task {task.id} for user {user.id} max pups:{user.max_puppies}")
                await session.commit()

        await asyncio.sleep(Config.dispatcher_delay)
