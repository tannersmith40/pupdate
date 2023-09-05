import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from back.lancaster.router import lancaster_router
from back.lancaster.utils import fill_proxy_table, task_dispatcher


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(lancaster_router)
# run task dispatcher as a background task
@app.on_event("startup")
async def app_startup():
    asyncio.create_task(task_dispatcher.run_dispatcher())


@app.on_event("startup")
async def startup():
    # await fill_proxy_table.create_proxy_records()
    ...


@app.on_event("shutdown")
async def shutdown():
    ...
