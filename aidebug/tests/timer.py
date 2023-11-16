from typing import Callable
import time

timer_switch = True


def function_timer(func: Callable) -> Callable:
    """
    A decorator that prints the function execution time in seconds. When applied to a function, this decorator 
    adds functionality to calculate the start and end time of execution, then it calculates the difference 
    between these which results in the time taken to execute the function. 

    Usage:
        @function_timer
        def test_function():
            ...

    Parameters:
        func (Callable): The function to time.

    Returns:
        Callable: The wrapped function. This function behaves exactly like the input function 'func', 
                  but with an additional printing of its execution time in seconds.
    """

    def wrapper(*args, **kwargs):
        # Reference the global switch
        global timer_switch
        if timer_switch:  # Check if timers should be active
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(
                f"Function {func.__name__} took {end_time - start_time} seconds to execute.")
            return result
        else:
            # If switch is off, execute the function without timing
            return func(*args, **kwargs)
    return wrapper
