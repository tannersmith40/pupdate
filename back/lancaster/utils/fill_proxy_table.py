from back.lancaster.utils.webshare import Webshare
from back.lancaster.manager import get_async_session
from back.lancaster.models import ProxyTable
from sqlalchemy import delete


async def create_proxy_records(country_code="US"):
    session = get_async_session()
    webshare = Webshare()

    proxy_list = webshare.get_filtered_by_country_proxy_list(country_code)
    async with session.begin():
        # Truncate the ProxyTable table
        await session.execute(delete(ProxyTable))
        # Create new ProxyTable records for each proxy in the list
        for proxy in proxy_list:
            proxy_record = ProxyTable(proxy=proxy)
            session.add(proxy_record)
        await session.commit()
    print(f"Proxy {len(proxy_list)} created")
    res = webshare.authorize_by_ip()
    print(f"Authorization result: {res}")
