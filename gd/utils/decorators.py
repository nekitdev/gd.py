def benchmark(func):
    def decorator(*args, **kwargs):
        import time
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        time_taken = (end-start)*1000
        thing = f'Executed "{func.__name__}(*args, **kwargs)";\n' \
            f'Args: {args}\nKwargs: {kwargs}\n' \
                f'Estimated time: {time_taken:.2f}ms.'
        print(thing)
        return res
    return decorator

class Abstract:
    """Brings subclasses different useful attributes."""
    def __init__(self):
        if not hasattr(self, '__to_repr__'):
            raise AttributeError("Any class subclassed from 'Abstract' should have attribute '__to_repr__' defined.")
        if not isinstance(self.__to_repr__, list):
            raise AttributeError("'Abstract' class expected '__to_repr__' as instance of 'list'. (Recieved '%s')" % type(self.__to_repr__).__name__)

    @property
    def __rmodule__(self):
        module = self.__module__
        return module.split('.')[0]

    @property
    def __name__(self):
        return self.__class__.__name__

    def __repr__(self):
        mapped = ', '.join(map(lambda a: f'{a}={getattr(self, a)}', self.__to_repr__))
        c = ': ' if len(mapped) > 0 else ''
        return '<{0.__rmodule__}.{0.__name__}'.format(self) + c + mapped + '>'

# TO_DO: Rename 'decorators.py' to 'wrap_tools.py'
