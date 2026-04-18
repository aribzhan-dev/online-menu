import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMPANY = "company"