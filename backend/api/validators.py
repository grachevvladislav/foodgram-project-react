import re

from rest_framework.exceptions import ValidationError

WRONG_SLUG_SYMBOLS = "Недопустимые символы: {}"


def slug_validator(value):
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(
            WRONG_SLUG_SYMBOLS.format(
                "".join(set(re.findall(r"[^\w.@+-]", value)))
            )
        )
    return value
