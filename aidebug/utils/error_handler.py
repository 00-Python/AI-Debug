import datetime
import logging
import traceback
from functools import wraps

def error_handler(func):
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'Error: {e}')

            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_message = str(e)
            traceback_message = traceback.format_exc()

            logging.error(f'{current_time} - {error_message}\n{traceback_message}')

            # Additional cleanup or error handling code can be added here

            return None

    return wrapper_function