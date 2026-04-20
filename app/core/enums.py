import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMPANY = "company"


class ThemeColor(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"