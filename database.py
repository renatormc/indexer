from pathlib import Path
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import Engine, create_engine


def make_engine() -> Engine:
    path = Path("index.sqlite3")
    return create_engine(f"sqlite:///{path}/meta.sqlite3")


class Base(DeclarativeBase):
    pass



def DBSession(path: Path) -> Session:
    return Session(make_engine(path), autocommit=False, autoflush=False)


def init_db(path: Path) -> None:
    eg = make_engine(path)
    Base.metadata.create_all(eg)


