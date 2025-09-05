from datetime import datetime
import hashlib
from pathlib import Path

from parser import extract_text_with_ocr
from repo import Document, Index


def index_pdf(index: Index, path: str | Path, index_timestamp: float | None = None) -> None:
    path = Path(path)
    pathstr = str(path).replace("\\", "/")
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    hash = sha256.hexdigest()
    doc = index.find_one("hash", hash)
    if doc and doc.path != pathstr:
        print("Path changed")
        doc.path = pathstr
        doc.title = path.name
        index.save_document(doc, index_timestamp=index_timestamp)
        return
    elif doc:
        print("nothing changed")
        if index_timestamp:
            index.save_document(doc,  index_timestamp=index_timestamp)
        return

    text = extract_text_with_ocr(path)
    doc = index.find_one("path", pathstr)
    if doc:
        print(doc)
        print("hash changed")
        doc.hash = hash
        doc.content = text
        index.save_document(doc, index_timestamp=index_timestamp)
        return

    print("new file")
    doc = Document(content=text, title=path.name, path=pathstr, year=2025, hash=hash)
    index.save_document(doc, index_timestamp=index_timestamp)


def update_index() -> None:
    index = Index()
    t = datetime.now().timestamp()
    for pdf_file in Path(".").rglob("*.pdf"):
        index_pdf(index, pdf_file, t)
        
