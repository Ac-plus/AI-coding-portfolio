class BookingError(Exception):
    """Base booking domain error."""


class RoomNotFoundError(BookingError):
    """Raised when a room cannot be found."""


class UserNotFoundError(BookingError):
    """Raised when a user cannot be found."""


class BookingNotFoundError(BookingError):
    """Raised when a booking cannot be found."""


class BookingConflictError(BookingError):
    """Raised when a booking overlaps with an existing one."""


class BookingValidationError(BookingError):
    """Raised when one or more booking rules are violated."""

    def __init__(self, errors: list[dict[str, str]]) -> None:
        super().__init__("Booking validation failed.")
        self.errors = errors
