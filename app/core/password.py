from fastapi import HTTPException, status


def validate_new_password(new_password: str, login: str | None = None) -> None:
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )

    if new_password.strip() != new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must not start or end with spaces"
        )

    if " " in new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must not contain spaces"
        )

    weak_passwords = {
        "123456",
        "12345678",
        "qwerty",
        "password",
        "admin123",
        "111111",
        "000000"
    }

    if new_password.lower() in weak_passwords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too weak"
        )

    if login and new_password.lower() == login.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must not be the same as login"
        )