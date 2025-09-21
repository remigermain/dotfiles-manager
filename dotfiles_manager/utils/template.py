import json

import jinja2
from jinja2 import Undefined


class SilentUndefined(Undefined):
    """
    Dont break pageloads because vars arent there!
    """

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""


environment = jinja2.Environment(undefined=SilentUndefined)


def read_file(file: str) -> dict:
    if file.endswith(".json"):
        with open(file) as f:
            return json.load(f)
    return {}


def template_file(content: str, flags) -> str:
    # # TODO keyring
    template = environment.from_string(content)

    conf = {}
    for config in flags.config:
        conf |= read_file(config)
    output = template.render(**conf)
    return output
