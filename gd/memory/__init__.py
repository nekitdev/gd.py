from gd.memory.base import Struct, Union
from gd.memory.fields import Field, I8, U8
from gd.memory.state import (
    AbstractState,
    DarwinState,
    State,
    SystemState,
    WindowsState,
    get_darwin_state,
    get_state,
    get_system_state,
    get_windows_state,
)
