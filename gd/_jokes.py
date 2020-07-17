from gd.typing import Any, Dict, Optional

__all__ = ("Jokes", "jokes")


class Jokes:
    def __repr__(self) -> str:
        return "<jokes>"

    def __getattr__(self, name: str) -> None:
        joke = self.get(name)

        if joke is not None:
            print(joke)

    def __setattr__(self, name: str, value: Any) -> None:
        mapping = self.__dict__

        if name in mapping:
            mapping[name] = value

        else:
            self.add(name, value)

    def get_all(self) -> Dict[str, str]:
        return joke_map

    def get(self, name: str) -> Optional[str]:
        return joke_map.get(name.lower())

    def add(self, name: str, joke: str) -> None:
        joke_map[str(name)] = str(joke)


jokes = Jokes()

joke_map = {
    "miko": "oh boy what name does she have this week",
    "nekit": "oh damn I missed a certain feature of gd in my api",
    "colon": "okay google comment something on my profile",
    "cos8o": "have you heard of hyperdash?",
    "cvolton": "what if we take gd, and make it so you get free rates from random people",
    "smjs": "does not like python",
    "101arrowz": "code cleaning 101",
    "absolute": "mega hack v5032 when",
    "adafcaefc": "we need more numbers in the progress bar",
    "alex": "loading everything at the same time != good code",
    "alex1304": "how are your codes so clean?",
    "alphalaneous": "let's interface gd",
    "blaze": "stop using mac",
    "devexit": "lol just beat zodiac",
    "italianapkdownloader": "let's hook super mario maker to gd",
    "mgostih": "smart and rust",
    "noah": "let's copy osu for all my design",
    "pavlukivan": "new gd codes are out: hold my beer",
    "pizzaroot": "asian student stereotype",
    "rya": "lol rebooting my gdps for the 80th time",
    "sputnix": "let's make gta5 in gd",
}
