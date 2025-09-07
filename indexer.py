from dataclasses import dataclass
from datetime import datetime
import hashlib
import logging
from pathlib import Path
from typing import Literal
from sqlalchemy import delete, or_
from sqlalchemy.orm import Session
from database import DBSession
from models import Document
from parser import extract_text_with_ocr
import fitz
from PIL import Image
from tqdm import tqdm


def generate_pdf_thumbnail(doc: Document, size=(200, 200)) -> None:
    thumbnail_path = doc.thumb
    if doc.thumb.is_file():
        return
    try:
        thumbnail_path.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    pdf_path = Path(doc.path)

    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[0]

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # type: ignore

    img.thumbnail(size, Image.LANCZOS)  # type: ignore

    img.save(thumbnail_path)
    pdf_doc.close()


def delete_thumbnail(doc: Document) -> None:
    try:
        doc.thumb.unlink()
    except FileNotFoundError:
        pass


@dataclass
class Res:
    doc: Document
    action:  Literal['same', 'moved', 'duplicated', 'new', 'modified']
    sha256: str


def calculate_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def analise_file(db_session: Session, path: str | Path) -> Res:
    path = Path(path)
    pathstr = path.as_posix()
    hash = calculate_hash(path)

    doc = db_session.query(Document).where(
        or_(
            Document.sha256 == hash,
            Document.path == pathstr
        )
    ).first()
    if not doc:
        return Res(Document(), "new", hash)
    if doc.sha256 == hash and doc.path == pathstr:
        return Res(doc, "same", hash)
    if doc.sha256 == hash and doc.path != pathstr:
        p = Path(doc.path)
        if p.is_file():
            return Res(Document(), "duplicated", hash)
        return Res(doc, "moved", hash)
    return Res(doc, "modified", hash)


def index_pdf(db_session: Session, path: str | Path, index_timestamp: float | None = None, commit=True) -> None:
    path = Path(path)
    res = analise_file(db_session, path)
    if res.action not in ['new', 'duplicated', 'same']:
        logging.info(f"{path} -> {res.action}")
    doc = res.doc
    if res.action == "modified":
        delete_thumbnail(doc)
        doc.sha256 = res.sha256
        doc.content = extract_text_with_ocr(path)
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        db_session.add(doc)
        generate_pdf_thumbnail(doc)
        if commit:
            db_session.commit()
    elif res.action == "moved":
        doc.path = str(path)
        doc.title = path.name
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        db_session.add(doc)
        generate_pdf_thumbnail(doc)
        if commit:
            db_session.commit()
    elif res.action == "same":
        if index_timestamp:
            if index_timestamp is not None:
                doc.index_timestamp = index_timestamp
            db_session.add(doc)
            generate_pdf_thumbnail(doc)
            if commit:
                db_session.commit()
    elif res.action == "new" or res.action == "duplicated":
        doc = Document()
        doc.content = extract_text_with_ocr(path)
        doc.title = path.name
        doc.path = path.as_posix()
        doc.sha256 = res.sha256
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        db_session.add(doc)
        if commit:
            db_session.commit()
        generate_pdf_thumbnail(doc)


def on_delete_file(db_session: Session, path: Path) -> None:
    doc = db_session.query(Document).where(Document.path == path.as_posix()).first()
    if doc:
        delete_thumbnail(doc)  
        db_session.delete(doc)  
        db_session.commit()


def update_index() -> None:
    with DBSession() as db_session:
        t = datetime.now().timestamp()
        pdf_files = list(Path(".").rglob("*.pdf"))
        for i, pdf_file in enumerate(tqdm(pdf_files, desc="Indexing PDFs")):
            index_pdf(db_session, pdf_file, t, commit=False)
            if i % 10 == 0:
                db_session.commit()
        db_session.commit()
        db_session.execute(delete(Document).where(Document.index_timestamp != t))
        db_session.commit()


def gen_thumbs() -> None:
    with DBSession() as db_session:
        docs = db_session.query(Document).all()
        for doc in docs:
            generate_pdf_thumbnail(doc)
