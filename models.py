from database import Base, make_engine
from sqlalchemy.orm import mapped_column, Mapped
import sqlalchemy as sa


class Document(Base):
    __tablename__ = 'document'
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.Text)
    content: Mapped[str] = mapped_column(sa.Text)
    meta: Mapped[str] = mapped_column(sa.Text, default="")
    sha256: Mapped[str] = mapped_column(sa.Text)
    path: Mapped[str] = mapped_column(sa.Text)


def create_fts():
    engine = make_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(title, content, content='documents', content_rowid='id');
        """))