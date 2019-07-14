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

def _make_repr(obj, info = []):
    module = obj.__module__.split('.')[0]  # for compability with other libraries
    name = obj.__class__.__name__
    if not info:
        return f'<{module}.{name}>'
    info = (', '.join('%s=%s' % t for t in info))
    return f'<{module}.{name}: {info}>'

# TO_DO: Rename 'decorators.py' to 'wrap_tools.py'
