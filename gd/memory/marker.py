__all__ = (
    "byte_t",
    "ubyte_t",
    "short_t",
    "ushort_t",
    "int_t",
    "uint_t",
    "long_t",
    "ulong_t",
    "longlong_t",
    "ulonglong_t",
    "int8_t",
    "uint8_t",
    "int16_t",
    "uint16_t",
    "int32_t",
    "uint32_t",
    "int64_t",
    "uint64_t",
    "intptr_t",
    "uintptr_t",
    "intsize_t",
    "uintsize_t",
    "float_t",
    "double_t",
    "float32_t",
    "float64_t",
    "bool_t",
)


class MarkerType:
    def __init__(self, name: str) -> None:
        self._name = name

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name


byte_t = MarkerType("byte_t")
ubyte_t = MarkerType("ubyte_t")
short_t = MarkerType("short_t")
ushort_t = MarkerType("ushort_t")
int_t = MarkerType("int_t")
uint_t = MarkerType("uint_t")
long_t = MarkerType("long_t")
ulong_t = MarkerType("ulong_t")
longlong_t = MarkerType("longlong_t")
ulonglong_t = MarkerType("ulonglong_t")

int8_t = MarkerType("int8_t")
uint8_t = MarkerType("uint8_t")
int16_t = MarkerType("int16_t")
uint16_t = MarkerType("uint16_t")
int32_t = MarkerType("int32_t")
uint32_t = MarkerType("uint32_t")
int64_t = MarkerType("int64_t")
uint64_t = MarkerType("uint64_t")

intptr_t = MarkerType("intptr_t")
uintptr_t = MarkerType("uintptr_t")
intsize_t = MarkerType("intsize_t")
uintsize_t = MarkerType("uintsize_t")

float_t = MarkerType("float_t")
double_t = MarkerType("double_t")

float32_t = MarkerType("float32_t")
float64_t = MarkerType("float64_t")

bool_t = MarkerType("bool_t")


# MarkerStruct
# MarkerUnion
