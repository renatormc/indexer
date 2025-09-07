from pathlib import Path
import config
from database import Base, make_engine
from sqlalchemy.orm import mapped_column, Mapped, Session
import sqlalchemy as sa


class Document(Base):
    __tablename__ = 'document'
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.Text)
    description: Mapped[str] = mapped_column(sa.Text, default="")
    content: Mapped[str] = mapped_column(sa.Text)
    sha256: Mapped[str] = mapped_column(sa.Text)
    path: Mapped[str] = mapped_column(sa.Text)
    loc: Mapped[str | None] = mapped_column(sa.Text)
    index_timestamp: Mapped[float] = mapped_column(sa.Float)

    @property
    def thumb(self) -> Path:
        return config.THUMBSDIR / f"{self.sha256}.png"

    @classmethod
    def search(cls, session: Session, query: str, limit: int | None = None):
        sql_text = """
            SELECT d.id, d.title, d.content, d.description, d.sha256, d.path, d.index_timestamp,
                   bm25(document_fts) AS rank
            FROM document_fts f
            JOIN document d ON d.id = f.rowid
            WHERE document_fts MATCH :query
            ORDER BY rank
        """

        if limit is not None:
            sql_text += " LIMIT :limit"

        sql = sa.text(sql_text)
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)

        result = session.execute(sql, params)
        return [
            cls(
                id=row.id,
                title=row.title,
                content=row.content,
                description=row.description,
                sha256=row.sha256,
                path=row.path,
                index_timestamp=row.index_timestamp
            )
            for row in result
        ]


def create_fts():
    engine = make_engine()
    with engine.connect() as conn:
        conn.execute(sa.text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts
            USING fts5(title, content, description, content='document', content_rowid='id');
        """))


def create_triggers():
    engine = make_engine()
    with engine.connect() as conn:
        conn.execute(sa.text("""
            CREATE TRIGGER IF NOT EXISTS document_ai AFTER INSERT ON document
            BEGIN
              INSERT INTO document_fts(rowid, title, content, description)
              VALUES (new.id, new.title, new.content, new.description);
            END;
        """))

        conn.execute(sa.text("""
            CREATE TRIGGER IF NOT EXISTS document_ad AFTER DELETE ON document
            BEGIN
              INSERT INTO document_fts(document_fts, rowid, title, content, description)
              VALUES('delete', old.id, old.title, old.content, old.description);
            END;
        """))

        conn.execute(sa.text("""
            CREATE TRIGGER IF NOT EXISTS document_au AFTER UPDATE ON document
            BEGIN
              INSERT INTO document_fts(document_fts, rowid, title, content, description)
              VALUES('delete', old.id, old.title, old.content, old.description);
              INSERT INTO document_fts(rowid, title, content, description)
              VALUES (new.id, new.title, new.content, new.description);
            END;
        """))


def init_db() -> None:
    try:
        config.INDEXDIR.mkdir()
    except FileExistsError:
        pass
    eg = make_engine()
    Base.metadata.create_all(eg)
    create_fts()
    create_triggers()

