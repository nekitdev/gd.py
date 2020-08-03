from gd.typing import TypeVar

T = TypeVar("T")


class Singleton:
    instance = None

    def __repr__(self) -> str:  # pragma: no cover
        return make_repr(self)

    @classmethod
    def __new__(cls, *args, **kwargs) -> T:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init__(*args, **kwargs)
        return cls.instance


class NULL(Singleton):
    pass


null = NULL()
