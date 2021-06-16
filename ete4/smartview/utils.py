
import time
from rich import print


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('[yellow]Time[/yellow] [green] %r [/green] %0.6f s' % (method.__name__, (te - ts)))
        return result
    return timed


# Customized exception.
class InvalidUsage(Exception):
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = 'Error: ' + message
        self.status_code = status_code
