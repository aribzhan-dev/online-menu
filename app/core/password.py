import re
from fastapi import HTTPException, status


def validate_new_password(new_password: str, login: str | None = None):
    if len(new_password) < 8:
        raise HTTPException(400, "Password too short")

    if not re.search(r"[A-Z]", new_password):
        raise HTTPException(400, "Must contain uppercase")

    if not re.search(r"[0-9]", new_password):
        raise HTTPException(400, "Must contain number")

    if " " in new_password:
        raise HTTPException(400, "No spaces allowed")

    if login and new_password.lower() == login.lower():
        raise HTTPException(400, "Password same as login")