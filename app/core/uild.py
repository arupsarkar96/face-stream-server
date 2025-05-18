import ulid
from sqlalchemy.types import TypeDecorator, CHAR

class ULIDType(TypeDecorator):
    impl = CHAR(26)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, ulid.ULID):
            return str(value)
        # Accept plain string input, assuming valid base32 ULID
        return str(ulid.ULID(value))  # ulid-py handles str inputs

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ulid.ULID(value)  # Accepts string as input
