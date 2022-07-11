import typing

import requests
from dotenv import load_dotenv
from starlette.testclient import AuthType, Cookies, DataType, FileType, Params
from starlette.testclient import TestClient as _TestClient
from starlette.testclient import TimeOut

from app import settings
from app.main import app


class TestClient(_TestClient):
    def __init__(self, app, api_version: str = settings.API_VERSION):
        super().__init__(app)
        self.api_version = api_version
        load_dotenv(".env.testing", override=True)

    def request(
        self,
        method: str,
        url: str,
        params: Params = None,
        data: DataType = None,
        headers: typing.MutableMapping[str, str] = None,
        cookies: Cookies = None,
        files: FileType = None,
        auth: AuthType = None,
        timeout: TimeOut = None,
        allow_redirects: bool = None,
        proxies: typing.MutableMapping[str, str] = None,
        hooks: typing.Any = None,
        stream: bool = None,
        verify: typing.Union[bool, str] = None,
        cert: typing.Union[str, typing.Tuple[str, str]] = None,
        json: typing.Any = None,
    ) -> requests.Response:
        url = f"/{self.api_version.rstrip('/')}{url}"
        return super().request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
        )


client = TestClient(app)
