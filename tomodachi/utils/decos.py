import asyncio
from functools import wraps
from typing import TypeVar, Optional, Any

from discord.ext import commands
from loguru import logger

__all__ = ["executor", "typing_indicator"]

T = TypeVar("T")


def executor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        logger.debug(f"Running {func.__name__}")
        future = loop.run_in_executor(None, lambda: func(*args, **kwargs))
        return future

    return wrapper


def typing_indicator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        executed: Optional[Any] = None

        for obj in set(args):
            if isinstance(obj, commands.Context):
                async with obj.typing():
                    executed = await func(*args, **kwargs)
                break
            else:
                continue

        return executed
    return wrapper