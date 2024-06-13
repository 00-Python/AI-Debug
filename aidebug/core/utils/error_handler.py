import datetime
import logging
import traceback
from functools import wraps
from typing import Callable

def error_handler(func: Callable) -> Callable:
    logging.basicConfig(
        filename='error.log',
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    @wraps(func)
    def wrapper_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print('User Exited!')
            raise
        except FileNotFoundError as fnf_error:
            print(f'File not found error: {fnf_error}')
            logging.error(traceback.format_exc())
        except PermissionError as pe_error:
            print(f'Permission error: {pe_error}')
            logging.error(traceback.format_exc())
        except ValueError as value_error:
            print(f'Value error: {value_error}')
            logging.error(traceback.format_exc())
        except KeyError as key_error:
            print(f'Key error: {key_error}')
            logging.error(traceback.format_exc())
        except IndexError as index_error:
            print(f'Index error: {index_error}')
            logging.error(traceback.format_exc())
        except TypeError as type_error:
            print(f'Type error: {type_error}')
            logging.error(traceback.format_exc())
        except AttributeError as attribute_error:
            print(f'Attribute error: {attribute_error}')
            logging.error(traceback.format_exc())
        except Exception as e:
            print(f'Error: {e}\nCheck the error.log file for more information...')
            logging.error(traceback.format_exc())
        return None

    return wrapper_function