from celery import Celery
import os
from scraper.scraper import LancasterPuppyScraper
from back.lancaster.models import UserScraperCredentials

broker_url = os.environ.get("BROKER_URL", "redis://localhost:6379/0")

app = Celery("tasks", broker=broker_url, backend="rpc://")


@app.task
def scrape_task(user_credentials: UserScraperCredentials, task_id: int):
    scraper = LancasterPuppyScraper(user_credentials=user_credentials, task_id=task_id)
    result = scraper.process()


if __name__ == "__main__":
    app.start()
