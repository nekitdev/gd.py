import functools
import inspect

from ..errors import (
    BadArgument, CommandException
)
from ..typing import (
    Any, Callable, Iterator, Optional, Set, Type
)
from ..utils.text_tools import make_repr

from .converters import (
    convert_to_bool
)

__all__ = ('Command', 'Group', 'GroupMixin', 'command', 'group')

Function = Callable[[Any], Any]


class Command:
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self._original_kwargs = kwargs.copy()
        return self

    def __init__(self, func: Callable, **kwargs) -> None:
        self.name = name = kwargs.get('name') or func.__name__

        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')

        self.callback = func

        help_doc = kwargs.get('help')

        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)

        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')

        self.help = help_doc

        self.brief = kwargs.get('brief')
        self.usage = kwargs.get('usage')

        self.aliases = kwargs.get('aliases', [])

        if not isinstance(self.aliases, (list, tuple)):
            raise TypeError('Aliases of a command must be a list or a tuple of strings.')

        self.description = inspect.cleandoc(kwargs.get('description', ''))

        self.parent = kwargs.get('parent')

    def __repr__(self) -> str:
        info = {
            'name': self.name,
            'callback': self.callback,
            'aliases': tuple(self.aliases)
        }
        return make_repr(self, info)

    @property
    def callback(self) -> Callable:
        return self._callback

    @callback.setter
    def callback(self, function: Callable) -> None:
        if not inspect.iscoroutinefunction(function):
            raise TypeError('Async function is required, got {0.__class__.__name__}.'.format(function))

        self._callback = function
        self.module = function.__module__

        signature = inspect.signature(function)
        self.params = signature.parameters.copy()

        for key, value in self.params.items():
            if isinstance(value.annotation, str):
                self.params[key] = value = value.replace(annotation=eval(value.annotation, function.__globals__))

    def update(self, **kwargs) -> None:
        self.__init__(self.callback, **{**self._original_kwargs, **kwargs})

    def copy(self):
         return self.__class__(self.callback, **self._original_kwargs)


class GroupMixin:
    def __init__(self, *args, **kwargs) -> None:
        self.all_commands = {}
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return make_repr(self, self.all_commands)

    @property
    def commands(self) -> Set[Command]:
        return set(self.all_commands.values())

    def recursively_remove_all_commands(self) -> None:
        for command in self.all_commands.copy().values():
            if isinstance(command, GroupMixin):
                command.recursively_remove_all_commands()
            self.remove_command(command.name)

    def add_command(self, command: Command) -> None:
        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command.')

        if isinstance(self, Command):
            command.parent = self

        if command.name in self.all_commands:
            raise CommandException('Command {0.name} is already registered.'.format(command))

        self.all_commands[command.name] = command

        for alias in command.aliases:
            if alias in self.all_commands:
                raise CommandException('The alias {} is already an existing command or alias.'.format(alias))

            self.all_commands[alias] = command

    def remove_command(self, name: str) -> Optional[Command]:
        command = self.all_commands.pop(name, None)

        # does not exist
        if command is None:
            return None

        if name in command.aliases:
            # we're removing an alias so we don't want to remove the rest
            return command

        # we're not removing the alias so let's delete the rest of them.
        for alias in command.aliases:
            self.all_commands.pop(alias, None)
        return command

    def walk_commands(self) -> Iterator[Command]:
        for command in tuple(self.all_commands.values()):
            yield command
            if isinstance(command, GroupMixin):
                yield from command.walk_commands()

    def get_command(self, name: str) -> Optional[Command]:
        # fast path, no space in name.
        if ' ' not in name:
            return self.all_commands.get(name)

        names = name.split()
        obj = self.all_commands.get(names[0])

        if not isinstance(obj, GroupMixin):
            return obj

        for name in names[1:]:
            try:
                obj = obj.all_commands[name]
            except (AttributeError, KeyError):
                return None

        return obj

    def command(self, *args, **kwargs) -> Function:
        def decorator(func: Function) -> Command:
            kwargs.setdefault('parent', self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(self, *args, **kwargs) -> Function:
        def decorator(func: Function) -> Group:
            kwargs.setdefault('parent', self)
            result = group(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator


class Group(GroupMixin, Command):
    """A class that implements a grouping protocol for commands to be
    executed as subcommands.

    This class is a subclass of :class:`.Command` and thus all options
    valid in :class:`.Command` are valid in here as well.

    Attributes
    -----------
    invoke_without_command: Optional[:class:`bool`]
        Indicates if the group callback should begin parsing and
        invocation only if no subcommand was found. Useful for
        making it an error handling function to tell the user that
        no subcommand was found or to have different functionality
        in case no subcommand was found. If this is ``False``, then
        the group callback will always be invoked first. This means
        that the checks and the parsing dictated by its parameters
        will be executed. Defaults to ``False``.
    case_insensitive: Optional[:class:`bool`]
        Indicates if the group's commands should be case insensitive.
        Defaults to ``False``.
    """
    def __init__(self, *args, **attrs) -> None:
        self.invoke_without_command = attrs.pop('invoke_without_command', False)
        super().__init__(*args, **attrs)

    def __repr__(self) -> str:
        return make_repr(self, self.all_commands)

    def copy(self):
        ret = super().copy()
        for cmd in self.commands:
            ret.add_command(cmd.copy())
        return ret


def command(cls: Optional[Type[Any]] = None, **kwargs) -> Function:
    if cls is None:
        cls = Command

    def decorator(func: Function) -> Command:
        if isinstance(func, Command):
            raise TypeError('Callback is already a command: {!r}.'.format(func))

        return cls(func, **kwargs)

    return decorator

def group(**attrs) -> Group:
    attrs.setdefault('cls', Group)
    return command(**attrs)
