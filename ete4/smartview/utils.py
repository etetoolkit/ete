import time
import random, string # generate random tree name if necessary


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(f'Time {method.__name__}   {te-ts}0.6f s')
        return result
    return timed


# Customized exception.
class InvalidUsage(Exception):
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = 'Error: ' + message
        self.status_code = status_code


def get_random_string(length):
    """ Generates random string to nameless trees """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

