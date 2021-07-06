from datetime import datetime

from corded import CordedClient, Route
from loguru import logger as _loguru_logger


TRACE = 0
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

_hook: str = None
_logger: "_Logger" = None
_level: int = INFO
_client: CordedClient = None


class _Logger:
    def __init__(self, level: int, webhook: str, client: CordedClient) -> None:
        self._level = level
        webhook = webhook.split("/")
        self._webhook_id = webhook[-2]
        self._webhook_token = webhook[-1]
        self._client = client

        self._route = Route("/webhooks/{webhook_id}/" + self._webhook_token, webhook_id=self._webhook_id)

    async def _send(self, level: str, message: str) -> None:
        await self._client.http.request(
            "POST",
            self._route,
            json={
                "content": f"`[{level.rjust(8)}]` `[{datetime.utcnow().isoformat()}]` {message}"[:2000]
            },
            expect="response",
        )

    def trace(self, message: str) -> None:
        if self._level > TRACE:
            return
        self._client.loop.create_task(self._send("TRACE", message))
        _loguru_logger.trace(message)

    def debug(self, message: str) -> None:
        if self._level > DEBUG:
            return
        self._client.loop.create_task(self._send("DEBUG", message))
        _loguru_logger.debug(message)

    def info(self, message: str) -> None:
        if self._level > INFO:
            return
        self._client.loop.create_task(self._send("INFO", message))
        _loguru_logger.info(message)

    def warning(self, message: str) -> None:
        if self._level > WARNING:
            return
        self._client.loop.create_task(self._send("WARNING", message))
        _loguru_logger.warning(message)

    def error(self, message: str) -> None:
        if self._level > ERROR:
            return
        self._client.loop.create_task(self._send("ERROR", message))
        _loguru_logger.error(message)

    def critical(self, message: str) -> None:
        if self._level > CRITICAL:
            return
        self._client.loop.create_task(self._send("CRITICAL", message))
        _loguru_logger.critical(message)


def set_hook(hook: str) -> None:
    global _hook
    _hook = hook

def set_level(level: int) -> None:
    global _level
    _level = level

def set_client(client: CordedClient) -> None:
    global _client
    _client = client

def get_logger() -> _Logger:
    if any([
        not _hook,
        not _client,
    ]): raise ValueError("You must use set_hook() and set_client() before using logging.")

    global _logger
    if not _logger:
        _logger = _Logger(_level, _hook, _client)
    return _logger
