from sqlalchemy import create_engine
from .models import Base


def init_db():
    try:
        engine = create_engine("sqlite:///kidlearnloop.db")
        Base.metadata.create_all(bind=engine)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    init_db()
