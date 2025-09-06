from typing import Iterable

from database import DBSession
from models import Document


def search_documents(query: str) -> Iterable[Document]:
    with DBSession() as db_session:
        return Document.search(db_session, query, 15)