from jinja2.ext import Extension


class ShoutExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["shout"] = lambda value: str(value).upper()
