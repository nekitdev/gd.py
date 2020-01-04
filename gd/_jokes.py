"""Module that implements some Geometry Dash jokes..."""

from .utils.text_tools import make_repr


class JokeHandler:
    def __init__(self) -> None:
        self.jokes = {
            'anime': 'I see, you are a person of culture.',
            'blaze': 'What if we would send all levels?',
            'colon': 'Did you use the right pusab?',
            'etzer': 'Have you sent it to RobTop yet? 8)',
            'michigun': 'Every level needs a triple... ΔΔΔ',
            'html': '<sarcasm> HTML is a programming language. </sarcasm>',
            'owo': 'Hewwo, my fwiend! owo',
            'serponge': 'New AlterGame in progress :pog:',
            'viprin': '[Ctrl+D] | [Ctrl+C & Ctrl+V]',
            'nekit': 'NeKit likes to code instead of school. )/'
        }

    def __repr__(self) -> str:
        info = {
            key: repr(value) for key, value in self.jokes.items()
        }
        return make_repr(self, info)

    def __getattr__(self, attr: str) -> None:
        name = attr.lower()

        if name not in self.jokes:
            return print('No joke was found under name: {!r}.'.format(attr))

        joke = str(self.jokes.get(name))
        print(joke)

    def add_joke(self, name: str, joke: str) -> None:
        new_joke = {name: joke}
        self.jokes.update(new_joke)


jokes = JokeHandler()
