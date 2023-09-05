from logging import getLogger
from abc import ABC, abstractmethod
import time
import os
import random
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.proxy import Proxy, ProxyType

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/89.0.774.45",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
]


class Website(ABC):
    def __init__(self,  proxy=None, logger=None):
        # # self.name = name
        # # self.credentials = credentials
        # self.db = db
        if logger:
            self.logger = logger
        else:
            self.logger = getLogger(__name__)
        self.proxy = proxy
        self.driver = self._set_driver()

        self.request_cookie = None
        self.cookie_string = None

    def _set_driver(self):
        options = self._get_options(proxy=self.proxy)
        if self.proxy:
            webdriver.DesiredCapabilities.CHROME["proxy"] = {
                "httpProxy": self.proxy,
                "ftpProxy": self.proxy,
                "sslProxy": self.proxy,
                "proxyType": "MANUAL",
            }
        # to prevent loading error  try 3 times if exception occurs sleep 1 minute and try again
        attempts = 0
        while attempts < 3:
            try:
                selenium_service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=selenium_service, options=options)
                self._execute_commands(driver)
                driver.maximize_window()
                return driver
            except Exception as e:
                attempts += 1
                self.logger.warning(f"Error while setting up driver: {e}")
                # self.logger.error(traceback.format_exc())
                self.logger.warning("Trying again in 1 minute")
                time.sleep(60)
        raise Exception("Could not set up driver")

    def _get_options(self, proxy:str):
        options = Options()
        # for local testing only
        if not os.getenv("LOCAL_TESTING"):
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument('--start-maximized')
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        # prefs = {
        #     "download.default_directory": str("."),
        #     "download.prompt_for_download": False,
        #     "profile.password_manager_enabled": False,
        #     "credentials_enable_service": False,
        # }
        prefs = {
            "safebrowsing_for_trusted_sources_enabled": False,
            # "download.default_directory": rf"{self.DOWNLOAD_DIR}/",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "profile.default_content_setting_values.popups": 2,
            # disable images
            "profile.managed_default_content_settings.images": 2
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("window-size=1920,1280")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        if proxy:
            options.add_argument("--proxy-server={}".format(proxy))
        return options

    def _execute_commands(self, driver):
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36"
            },
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def take_screenshot(self, filename):
        screenshot_folder = 'scraper/debug'
        # transform filename to be a valid filename
        filename = "".join(x for x in filename if x.isalnum() or x in [" ", "_", "."]).rstrip()
        filename = f"{screenshot_folder}/{filename}"
        try:
            self.driver.save_screenshot(filename)
            self.logger.warning(f"Screenshot saved as {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {e}")

    def wait_element(self, wait_by, waiting_xpath: str, timeout: int = 90):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((wait_by, waiting_xpath))
            )
        except TimeoutException:
            self.logger.error(f"Waiting {wait_by} {waiting_xpath} element timeout")
            self.take_screenshot( f"timeout_{wait_by}_{waiting_xpath}.png")
            raise

    # wait button to be clickable and click it
    def wait_and_click(self, wait_by, waiting_xpath: str, timeout=90, raise_exception=True):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((wait_by, waiting_xpath))
            )
            button = self.driver.find_element(wait_by, waiting_xpath)

            actions = ActionChains(self.driver)
            actions.move_to_element(button)

            # Add some human-like inaccuracy to the movement
            # x_offset = random.randint(-5, 5)
            # y_offset = random.randint(-5, 5)
            # actions.move_by_offset(x_offset, y_offset)

            # Scroll to the button
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            return True
        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(f"Waiting {wait_by} {waiting_xpath} element timeout")
            self.take_screenshot(f"timeout_{wait_by}_{waiting_xpath}.png")
            if raise_exception:
                raise
            return False

    def get_cookie(self, cookies):
        cookie_string = ""
        for cookie in cookies:
            name = cookie["name"]
            value = cookie["value"]
            cookie_string += f"{name}={value}; "
        self.cookie_string = cookie_string[:-2]

        print("Cookie obtained!")
        return self.cookie_string
