"""Bounded document validation and private, exclusive file creation."""
import os
import secrets
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from defusedxml import ElementTree
from flask import current_app
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


def read_document(upload, allowed=(".pdf",)):
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in allowed:
        raise ValueError("Please choose a PDF or DOCX document.")
    maximum = current_app.config["MAX_UPLOAD_BYTES"]
    data = upload.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("Please choose a file under 10 MB.")
    if not data:
        raise ValueError("Please choose a readable document.")
    try:
        if suffix == ".pdf":
            _validate_pdf(data)
        else:
            _validate_docx(data)
    except Exception as exc:
        raise ValueError("Please choose a readable PDF or DOCX without scripts, macros, or embedded files.") from exc
    return data, suffix


def _validate_pdf(data):
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-2048:]:
        raise ValueError("Invalid PDF")
    reader = PdfReader(BytesIO(data), strict=True)
    if reader.is_encrypted or not 1 <= len(reader.pages) <= 500:
        raise ValueError("Unsupported PDF")
    pending = [reader.trailer]
    seen = set()
    nodes = 0
    forbidden = {"/JS", "/JavaScript", "/AA", "/OpenAction", "/EmbeddedFiles", "/RichMedia", "/XFA"}
    while pending:
        obj = pending.pop()
        nodes += 1
        if nodes > 10000:
            raise ValueError("Document too complex")
        if isinstance(obj, IndirectObject):
            ref = (obj.idnum, obj.generation)
            if ref in seen:
                continue
            seen.add(ref)
            pending.append(obj.get_object())
        elif isinstance(obj, DictionaryObject):
            if forbidden.intersection(obj) or obj.get("/Type") == "/EmbeddedFile" or obj.get("/S") in ("/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData"):
                raise ValueError("Active document content")
            pending.extend(obj.values())
        elif isinstance(obj, ArrayObject):
            pending.extend(obj)


def _validate_docx(data):
    with ZipFile(BytesIO(data)) as archive:
        entries = archive.infolist()
        names = {entry.filename for entry in entries}
        if not {"[Content_Types].xml", "word/document.xml"}.issubset(names) or len(entries) > 2000:
            raise BadZipFile("Not a Word document")
        if sum(entry.file_size for entry in entries) > 30 * 1024 * 1024:
            raise BadZipFile("Expanded document too large")
        for entry in entries:
            name = entry.filename.lower()
            if "\\" in name or name.startswith("/") or ".." in name.split("/") or entry.flag_bits & 1:
                raise BadZipFile("Unsafe archive entry")
            if any(part in name for part in ("vbaproject", "embeddings/", "activex/")):
                raise BadZipFile("Active document content")
            if entry.file_size > 10 * 1024 * 1024 or entry.file_size > max(entry.compress_size, 1) * 1000:
                raise BadZipFile("Unsafe compression")
            if name.endswith((".xml", ".rels")):
                root = ElementTree.fromstring(archive.read(entry))
                if name.endswith(".rels") and any(item.attrib.get("TargetMode") == "External" for item in root):
                    raise BadZipFile("External document relationship")
                if name == "[content_types].xml" and any("macroenabled" in str(item.attrib).lower() for item in root):
                    raise BadZipFile("Macro document")


def cv_folder():
    folder = Path(current_app.config.get("CV_STORAGE_FOLDER") or Path(current_app.root_path).parent / "uploads" / "cvs")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    return folder.resolve()


def store_cv(data, suffix):
    filename = secrets.token_hex(32) + suffix
    path = cv_folder() / filename
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(data)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return filename
