from typing import List, Dict, Any, Union, Optional
import requests
from back.lancaster.config import Config


class Webshare:
    def __init__(self):
        self.api_key = Config.webshare_api_key
        self.ip_check_url = "https://api.myip.com"

    def get_proxy_list(self):
        proxy_list = []
        url = f"https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25"
        while True:
            response = requests.get(
                url,
                headers={"Authorization": f"Token {self.api_key}"},
            )
            result = response.json()
            proxy_list.extend(result["results"])
            if result["next"]:
                url = result["next"]
            else:
                break

        return proxy_list

    def check_my_ip(self, proxy: str = None) -> Dict:
        proxy = {"http": proxy, "https": proxy}
        response = requests.get(self.ip_check_url, proxies=proxy)
        return response.json()

    def is_proxy_working(self, proxy_item: Dict) -> bool:
        port = (
            proxy_item["ports"]["http"]
            if proxy_item.get("ports")
            else proxy_item["port"]
        )
        proxy = f'{proxy_item["proxy_address"]}:{port}'
        my_new_ip = self.check_my_ip(proxy=proxy)
        if my_new_ip["ip"] == proxy_item["proxy_address"]:
            return True
        return False

    def authorize_by_ip(self) -> bool:
        my_ip = self.check_my_ip()
        proxy_list = self.get_proxy_list()
        # List IP Authorization
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/ipauthorization/",
            headers={"Authorization": f"Token {self.api_key}"},
        )
        list_ip_auth = response.json()
        if list_ip_auth["results"]:
            if list(
                filter(
                    lambda x: x["ip_address"] == my_ip["ip"], list_ip_auth["results"]
                )
            ):
                # already authorized
                return self.is_proxy_working(proxy_list[0])
            else:
                # Delete first IP authorization
                response = requests.delete(
                    f"https://proxy.webshare.io/api/v2/proxy/ipauthorization/{list_ip_auth['results']['id']}/",
                    headers={"Authorization": f"Token {self.api_key}"},
                )

        # Create IP authorization
        response = requests.post(
            "https://proxy.webshare.io/api/v2/proxy/ipauthorization/",
            headers={"Authorization": f"Token {self.api_key}"},
            json={"ip_address": my_ip["ip"]},
        )
        if response.json().get("ip_address") == my_ip["ip"]:

            # Success
            return self.is_proxy_working(proxy_list[0])
        return False

    def get_filtered_by_country_proxy_item_list(
        self, country_code: str
    ) -> List[Dict[str, Any]]:
        proxy_list = self.get_proxy_list()

        return list(filter(lambda x: x["country_code"] == country_code, proxy_list))

    def get_filtered_by_country_proxy_list(self, country_code: str) -> List[str]:
        proxy_item_list = self.get_proxy_list()
        proxy_list = list()

        for proxy_item in list(
            filter(lambda x: x["country_code"] == country_code, proxy_item_list)
        ):
            port = (
                proxy_item["ports"]["http"]
                if proxy_item.get("ports")
                else proxy_item["port"]
            )
            proxy = f'{proxy_item["proxy_address"]}:{port}'
            proxy_list.append(proxy)
        return proxy_list
