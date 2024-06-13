from typing import Callable
import time

timer_switch = True

def function_timer(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        if timer_switch:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {end_time - start_time} seconds to execute.")
            return result
        else:
            return func(*args, **kwargs)
    return wrapper