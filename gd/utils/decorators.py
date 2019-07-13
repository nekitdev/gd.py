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
    def __init__(self):
        if not hasattr(self, '__to_repr__'):
            self.__to_repr__ = []
        if not isinstance(self.__to_repr__, list):
            raise AttributeError("'Abstract' class expected '__to_repr__' as instance of 'list'. (recieved '%s')" % type(self.__to_repr__).__name__)

    @property
    def __rmodule__(self):
        module = self.__module__
        return module.split('.')[0]

    @property
    def __name__(self):
        return self.__class__.__name__

    def __repr__(self):
        to_repr = [(name, getattr(self, name)) for name in self.__to_repr__]
        str_repr = ', '.join('%s=%s' % t for t in to_repr)
        additional = ': ' if len(str_repr) > 0 else ''
        return '<{0.__rmodule__}.{0.__name__}{1}{2}>'.format(self, additional, str_repr)

# TO_DO: Rename 'decorators.py' to 'wrap_tools.py'
