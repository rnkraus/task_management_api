from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local", override=True)

from app.core.db import SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.task import Task  # noqa: E402, F401


def make_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"User with email '{email}' not found")
            return

        user.role = "admin"
        db.commit()

        print(f"User '{email}' is now an admin")

    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m scripts.make_admin <email>")
        sys.exit(1)

    email = sys.argv[1]
    make_admin(email)