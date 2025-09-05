from dataclasses import dataclass, field
from pathlib import Path
import shutil
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser
import os
from uuid import uuid4


@dataclass
class Document:
    year: int
    path: str
    id: str | None = None
    hash: str = ""
    title: str = ""
    tags: list[str] = field(default_factory=list)
    content: str = ""
    index_timestamp: float = 0.0


class Index:
    index_dir = Path("indexdir")

    def __init__(self):
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            tags=KEYWORD(stored=True, commas=True, lowercase=True),
            year=NUMERIC(stored=True),
            content=TEXT(stored=False),
            path=TEXT(stored=True),
            hash=TEXT(stored=True),
            index_timestamp=NUMERIC(stored=True),
        )
        self.ix = self.open_index()
        self.writer = self.ix.writer()

    @classmethod
    def clear(cls) -> None:
        try:
            shutil.rmtree(cls.index_dir)
        except FileNotFoundError:
            pass

    def open_index(self) -> index.FileIndex:
        if not self.index_dir.is_dir():
            self.index_dir.mkdir()
            return index.create_in(str(self.index_dir), self.schema)
        return index.open_dir(str(self.index_dir))

    def search(self, query: str, limit=10):
        with self.ix.searcher() as searcher:
            query = QueryParser("content", self.ix.schema).parse(query)
            for res in searcher.search(query, limit=10):
                yield Document(**res)

    def find_one(self, field: str, query_str: str) -> Document | None:
        with self.ix.searcher() as searcher:
            parser = QueryParser(field, schema=self.ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query, limit=1)
            if results:
                return Document(**results[0])
            return None

    def save_document(self, doc: Document, index_timestamp: float | None = None, commit=True) -> None:
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        if doc.id is None:
            doc.id = uuid4().hex
            self.writer.add_document(
                id=doc.id,
                title=doc.title,
                tags=",".join(doc.tags),
                year=doc.year,
                content=doc.content,
                path=doc.path.replace("\\", "/"),
                hash=doc.hash,
                index_timestamp=index_timestamp if index_timestamp is not None else doc.index_timestamp
            )
        else:
            self.writer.update_document(
                id=doc.id,
                title=doc.title,
                tags=",".join(doc.tags),
                year=doc.year,
                content=doc.content,
                path=doc.path.replace("\\", "/"),
                hash=doc.hash,
                index_timestamp=index_timestamp if index_timestamp is not None else doc.index_timestamp
            )
        if commit:
            self.writer.commit()

    def commit(self) -> None:
        self.writer.commit()
