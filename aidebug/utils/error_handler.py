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
            print(f'Error: {e}\nCheck the error.log file for more information...')

            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_message = str(e)
            traceback_message = traceback.format_exc()

            logging.error(f'{current_time} - {error_message}\n{traceback_message}')

            # Additional cleanup or error handling code can be added here
        except KeyboardInterrupt as e:
            print('User Exited!')
            raise
        except FileNotFoundError as fnf_error:
            print(f'File not found error: {fnf_error}')
        except PermissionError as pe_error:
            print(f'Permission error: {pe_error}')
        except ValueError as value_error:
            print(f'Value error: {value_error}')
        except KeyError as key_error:
            print(f'Key error: {key_error}')
        except IndexError as index_error:
            print(f'Index error: {index_error}')
        except TypeError as type_error:
            print(f'Type error: {type_error}')
        except AttributeError as attribute_error:
            print(f'Attribute error: {attribute_error}')

            return None

    return wrapper_function