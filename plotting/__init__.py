from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import matplotlib

P = ParamSpec("P")
T = TypeVar("T")


def styled(path: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with matplotlib.rc_context(fname=path):
                return func(*args, **kwargs)

        return wrapper

    return decorator
