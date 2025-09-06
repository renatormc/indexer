from pathlib import Path
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import Engine, create_engine

import config


def make_engine() -> Engine:
    return create_engine(f"sqlite:///{config.SQLITE_FILE}")


class Base(DeclarativeBase):
    pass



def DBSession() -> Session:
    return Session(make_engine(), autocommit=False, autoflush=False)





