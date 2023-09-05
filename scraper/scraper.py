import logging
import pytz
from selenium.webdriver.common.by import By

try:
    from scraper.website import Website
except:
    from website import Website
import time
import imaplib
from datetime import datetime
import re
from contextlib import contextmanager
import email
from email.header import decode_header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, create_engine, func
from back.lancaster.manager import db_manager, DBManager
from back.lancaster.config import db_config
from back.lancaster.models import (
    UserScraperCredentials,
    LogTable,
    ScrapingTaskTable,
    TaskStatusEnum,
    TaskResultEnum,
)


class ScraperException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class LogTableHandler(logging.Handler):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def emit(self, record):
        log = LogTable(
            user_id=record.user_id,
            timestamp=datetime.utcnow(),
            level=record.levelname,
            message=record.getMessage(),
        )
        self.session.add(log)
        self.session.commit()


# function to get the current time in EDT
def current_time_in_edt(*args):
    utc_dt = datetime.utcnow().replace(tzinfo=pytz.utc)
    edt_dt = utc_dt.astimezone(pytz.timezone("US/Eastern"))
    return edt_dt.timetuple()


class LogManager:
    def __init__(self, session: Session, user_id: int):
        self.session = session
        self.user_id = user_id

    def get_logger(self, user_id, name="run_logs"):
        LOG_FOLDER = "scraper/log"
        formatter = logging.Formatter(
            f"%(asctime)s [%(levelname)s] [User: {user_id}]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        formatter.converter = current_time_in_edt
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s]: %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.user_id = self.user_id
            return record

        logging.setLogRecordFactory(record_factory)
        log_file = f"{name}.log"

        logger = logging.getLogger(name)
        if not logger.handlers:  # check if logger has handlers
            file_handler = logging.FileHandler(
                f"{LOG_FOLDER}/{log_file}", encoding="utf-8"
            )
            db_handler = LogTableHandler(self.session)

            file_handler.setLevel(logging.NOTSET)
            file_handler.setFormatter(formatter)

            db_handler.setLevel(logging.NOTSET)
            db_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(db_handler)

        return logger


class LancasterPuppyScraper:
    def __init__(self, user_credentials, task_id: int):
        self.task_id = task_id
        self.user_credentials = user_credentials
        self.website = None
        # self.logger = self.get_logger("lancaster")
        # self.db_manager = DBManager(db_url=db_config.dsn)
        self.db = create_engine(
            db_config.dsn,
            echo=False,
        )
        # create session from engine self.db
        self.session = Session(self.db)
        log_manager = LogManager(self.session, user_credentials["user_id"])

        self.logger = log_manager.get_logger(user_id=user_credentials["user_id"])
        # self.session = db_manager.get_session()

    @contextmanager
    def time_profile(self, label=""):
        start = time.time()
        try:
            yield
        finally:
            end = time.time()
            self.logger.info(f"{label}: {int(end - start)} sec")

    def delete_mail(self, imap, email_id):
        username = self.user_credentials["gmail_username"]
        password = self.user_credentials["gmail_password"]
        while True:
            try:
                r = imap.uid("store", email_id, "+X-GM-LABELS", "\\Trash")
            except imaplib.IMAP4.abort:
                imap = imaplib.IMAP4_SSL("imap.gmail.com")
                imap.login(username, password)
                imap.select("Inbox")
                # print("imaplib.IMAP4.abort: command: UID => socket error: EOF")
                continue
            break
        r = imap.expunge()

    def read_last_email_from_gmail_after_time(
        self, sender_email, after_time: str
    ) -> str:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")

        username = self.user_credentials["gmail_username"]
        password = self.user_credentials["gmail_password"]
        imap.login(username, password)
        imap.select("inbox")

        after_datetime = datetime.strptime(after_time, "%Y-%m-%d %H:%M:%S")

        search_criteria = (
            # f'(FROM {sender_email} SINCE {after_datetime.strftime("%d-%b-%Y")})'
            f"(FROM {sender_email})"
        )
        while True:
            imap.select("inbox")
            status, response = imap.uid("search", None, search_criteria)
            if response[0] != b"":
                break
            time.sleep(2)
            continue

        email_ids = response[0].split()
        latest_email_id = email_ids[-1]

        # fetch the last email from the sender that matches the search criteria
        status, email_data = imap.uid("fetch", latest_email_id, "(RFC822)")

        raw_email = email_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # extract the body of the email
        subject = decode_header(email_message["Subject"])[0][0]
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                body = part.get_payload(decode=True).decode()
                if body:
                    break
        else:
            body = email_message.get_payload(decode=True).decode()

        self.delete_mail(imap, latest_email_id)
        # close the connection
        imap.close()
        imap.logout()
        return body

    def extract_one_time_password_from_email(self, current_time):
        sender_email = "admin@lancasterpuppies.com"
        email_body = self.read_last_email_from_gmail_after_time(
            sender_email=sender_email, after_time=current_time
        )
        one_time_password = None
        one_time_password = re.findall("Verification code: \*([0-9]{6})\*", email_body)[
            0
        ]
        self.logger.info(f"One time password: {one_time_password}")
        return one_time_password

    def login(self):
        self.website.driver.get("https://www.lancasterpuppies.com/user/login")
        # save page content to file
        with open("scraper/debug/login.html", "w") as f:
            f.write(self.website.driver.page_source)

        self.website.driver.implicitly_wait(50)
        self.website.take_screenshot("before_login.png")
        self.website.wait_element(By.XPATH, '//button[@id="edit-submit"]')
        username_box = self.website.driver.find_element(
            By.XPATH, '//*[@id="edit-name"]'
        )
        password_box = self.website.driver.find_element(
            By.XPATH, '//*[@id="edit-pass"]'
        )
        login_button = self.website.driver.find_element(
            By.XPATH, "//*[@id='edit-submit']"
        )

        username_box.send_keys(self.user_credentials["lancaster_email"])
        password_box.send_keys(self.user_credentials["lancaster_password"])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        login_button.click()

        # sometimes, program skips 2FA, if this happened, return
        time.sleep(3)
        self.website.driver.implicitly_wait(15)
        self.website.take_screenshot("login-after-creds.png")
        if self.website.driver.find_elements(By.CSS_SELECTOR, "a[href='/user']"):
            self.logger.info(
                f"Login as {self.user_credentials['lancaster_email']} successful"
            )
            return True
        else:
            if "Have you forgotten your password?" in self.website.driver.page_source:
                self.website.take_screenshot("login-2fa.png")
                raise ScraperException("unrecognized Lancaster username or password")
        self.website.wait_element(By.XPATH, '//*[@id="edit-code"]')
        otp_code = self.extract_one_time_password_from_email(current_time)
        otp_box = self.website.driver.find_element(By.XPATH, '//*[@id="edit-code"]')
        otp_box.send_keys(otp_code)
        submit_button = self.website.driver.find_element(
            By.XPATH, '//*[@id="edit-login"]'
        )
        submit_button.click()
        self.website.driver.implicitly_wait(15)
        if "Invalid code" in self.website.driver.page_source:
            raise ScraperException("Invalid OTP code")

    def set_task_status(
        self,
        status: TaskStatusEnum,
        task_result: TaskResultEnum = None,
        detail: str = None,
        date_start: bool = None,
        date_end: bool = None,
    ):
        if not self.task_id:
            return False
        result = self.session.execute(
            select(ScrapingTaskTable).where(ScrapingTaskTable.id == self.task_id)
        )
        scraping_task = result.scalars().first()
        scraping_task.current_status = status.value
        if task_result:
            scraping_task.task_result = task_result.value
        if detail:
            scraping_task.task_result_detail = detail
        if date_start:
            scraping_task.date_start = datetime.now()
        if date_end:
            scraping_task.date_end = datetime.now()
        self.session.commit()

    def process(self):
        try:
            with self.time_profile("Completed in"):
                self.website = Website(
                    proxy=self.user_credentials["proxy"], logger=self.logger
                )

                # self.website.driver.get("https://api.myip.com")
                # print(self.website.driver.page_source)
                # with open("scraper/debug/ip.html", "w") as f:
                #     f.write(self.website.driver.page_source)

                self.logger.info("")
                self.logger.info(
                    f"Updating { self.user_credentials['lancaster_email']} pups:{self.user_credentials['max_puppies']}"
                )
                self.set_task_status(
                    status=TaskStatusEnum.RUNNING,
                    task_result=TaskResultEnum.PENDING,
                    date_start=True,
                )

                self.login()
                # self.logger.info("Login successful")
                ads_list = list()
                self.website.wait_and_click(By.LINK_TEXT, "My Account Links")
                self.website.wait_and_click(By.LINK_TEXT, "Manage My Current Ads")
                first_page_ads_list = [
                    order.get_attribute("href")
                    for order in self.website.driver.find_elements(
                        By.XPATH,
                        "//tr/child::td[@class='views-field views-field-flagged' and contains(text(),'No')]/following-sibling::td[@class='views-field views-field-title']/a",
                    )
                ]
                #
                if not first_page_ads_list:
                    raise ScraperException("There don't seem to be any ads.")
                if self.website.driver.find_elements(By.LINK_TEXT, "last »"):
                    self.website.wait_and_click(By.LINK_TEXT, "last »")
                while True:
                    # skip first page, so already fetched
                    if self.website.driver.find_elements(By.LINK_TEXT, "‹ previous"):
                        for order in self.website.driver.find_elements(
                            By.XPATH,
                            "//tr/child::td[@class='views-field views-field-flagged' and contains(text(),'No')]/following-sibling::td[@class='views-field views-field-title']/a",
                        ):
                            ads_list.append(order.get_attribute("href"))
                        self.website.wait_and_click(By.LINK_TEXT, "‹ previous")
                        self.website.wait_element(By.CLASS_NAME, "email-link")
                        continue
                    break
                ads_list.extend(first_page_ads_list)
                self.logger.info(f"{len(ads_list)} puppies to update")
                for idx, ads_url in enumerate(ads_list, start=1):
                    page_title = self.process_puppy_ad(ads_url)
                    self.logger.info(f"Updated {idx}/{len(ads_list)}: {page_title}")
                    if (
                        self.user_credentials["max_puppies"]
                        and idx >= self.user_credentials["max_puppies"]
                    ):
                        break

                self.set_task_status(
                    status=TaskStatusEnum.STOPPED,
                    task_result=TaskResultEnum.SUCCESS,
                    date_end=True,
                )
            return idx
        except ScraperException as e:
            self.logger.error(e.message)
            self.set_task_status(
                status=TaskStatusEnum.STOPPED,
                task_result=TaskResultEnum.FAILED,
                detail=str(e.message),
                date_end=True,
            )
        except Exception as e:
            # import traceback
            # print(traceback.format_exc())
            # TODO: Error: Message: unknown error: net::ERR_TUNNEL_CONNECTION_FAILED
            self.logger.error(f"Error: {e}")
            self.website.driver.quit()
            self.set_task_status(
                status=TaskStatusEnum.STOPPED,
                task_result=TaskResultEnum.FAILED,
                detail=str(e),
                date_end=True,
            )
        finally:
            self.session.close()
            self.db.dispose()
            if self.website and self.website.driver:
                self.website.driver.quit()

    def process_puppy_ad(self, url_order):
        self.website.driver.get(url_order)
        self.website.wait_element(By.LINK_TEXT, "Edit")
        page_title = self.website.driver.find_element(
            By.XPATH, "//h1[@class='page-title']"
        ).text
        self.website.wait_and_click(By.LINK_TEXT, "Edit")
        self.website.wait_and_click(By.ID, "edit-submit", raise_exception=True)
        return page_title


if __name__ == "__main__":
    user_credentials = UserScraperCredentials(
        user_id=1,
        lancaster_email="wonderfulpuppies99@gmail.com",
        lancaster_password="Wednesday2@",
        gmail_username="wonderfulpuppies99@gmail.com",
        gmail_password="lnosaukrwesouqhv",
        max_puppies=None,
        proxy="",
    )
    scraper = LancasterPuppyScraper(
        user_credentials=user_credentials.dict(), task_id=52
    )
    scraper.process()
