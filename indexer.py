from datetime import datetime
import hashlib
from pathlib import Path
from sqlalchemy import delete
from sqlalchemy.orm import Session
import config
from database import DBSession
from models import Document
from parser import extract_text_with_ocr
import fitz 
from PIL import Image

def generate_pdf_thumbnail(doc: Document, size=(200, 200)) -> None:
    thumbnail_path = doc.thumb
    if doc.thumb.is_file():
        return
    try:
        thumbnail_path.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    pdf_path = Path(doc.path)
    print(f"Gerando thumbnail: {doc.title}")

    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[0]

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) #type: ignore

    img.thumbnail(size, Image.LANCZOS)  #type: ignore

    img.save(thumbnail_path)
    pdf_doc.close()

def delete_thumbnail(doc: Document) -> None:
    try:
        doc.thumb.unlink()
    except FileNotFoundError:
        pass


def index_pdf(db_session: Session, path: str | Path, index_timestamp: float | None = None, commit=True) -> None:
    path = Path(path)
    pathstr = str(path).replace("\\", "/")
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    hash = sha256.hexdigest()
    doc = db_session.query(Document).where(Document.sha256 == hash).first()
    if doc and doc.path != pathstr:
        print("Path changed")
        doc.path = pathstr
        doc.title = path.name
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        db_session.add(doc)
        generate_pdf_thumbnail(doc)
        if commit:
            db_session.commit()
        return
    elif doc:
        print("nothing changed")
        if index_timestamp:
            if index_timestamp is not None:
                doc.index_timestamp = index_timestamp
            db_session.add(doc)
            generate_pdf_thumbnail(doc)
            if commit:
                db_session.commit()
        return

    text = extract_text_with_ocr(path)
    doc = db_session.query(Document).where(Document.path == pathstr).first()
    if doc:
        print("hash changed")
        delete_thumbnail(doc)
        doc.sha256 = hash
        doc.content = text
        if index_timestamp is not None:
            doc.index_timestamp = index_timestamp
        db_session.add(doc)
        generate_pdf_thumbnail(doc)
        if commit:
            db_session.commit()
        return

    print("new file")
    doc = Document(content=text, title=path.name, path=pathstr, sha256=hash)
    if index_timestamp is not None:
        doc.index_timestamp = index_timestamp
    db_session.add(doc)
    if commit:
        db_session.commit()
    generate_pdf_thumbnail(doc)
    


def update_index() -> None:
    with DBSession() as db_session:
        t = datetime.now().timestamp()
        for i, pdf_file in enumerate(Path(".").rglob("*.pdf")):
            index_pdf(db_session, pdf_file, t, commit=False)
            if i%10 == 0:
                db_session.commit()
            print(i)
        db_session.commit()
        db_session.execute(delete(Document).where(Document.index_timestamp != t))
        db_session.commit()
        

def gen_thumbs() -> None:
    with DBSession() as db_session:
        docs = db_session.query(Document).all()
        for doc in docs:
            generate_pdf_thumbnail(doc)