from pydantic import BaseSettings


class APIConfig(BaseSettings):
    # webshare_api_key: str = "1t5519lfuzf329nnu5aunzgmn1i6be6o55ttms7b"
    webshare_api_key: str = "konqbvp658mfz1cuczf7bnk48iewq1bzj88r1xl7"
    dispatcher_delay: int = 60
    class Config:
        fields = {
            "webshare_api_key": {"env": "WEBSHARE_API_KEY"},
        }

Config = APIConfig(_env_file=".env", _env_file_encoding="utf-8")



class DBConfig(BaseSettings):
    dsn: str = "postgresql://postgres:postgres@db:5432/lancaster"
    dsn_async: str = "postgresql+asyncpg://postgres:postgres@db:5432/lancaster"

    class Config:
        fields = {
            "dsn": {"env": "DSN"},
            "dsn_async": {"env": "DSN_ASYNC"},
        }


db_config = DBConfig(_env_file=".env", _env_file_encoding="utf-8")
