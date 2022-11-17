import re

from rest_framework.exceptions import ValidationError

WRONG_USERNAME = '"me" - недопустимое имя пользователя!'
WRONG_SYMBOLS = "Недопустимые символы: {}"


def username_validator(value):
    """
    username != 'me'
    username includes only letters, digits and @/./+/-/_
    """
    if value == 'me':
        raise ValidationError(WRONG_USERNAME)
    if not re.fullmatch(r'^[\w.@+-]+', value):
        raise ValidationError(
            WRONG_SYMBOLS.format(
                "".join(set(re.findall(r"[^\w.@+-]", value)))
            )
        )
    return value
