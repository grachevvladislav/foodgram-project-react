from users.validators import username_validator


class UsernameMixins:
    def validate_username(self, value):
        return username_validator(value)
