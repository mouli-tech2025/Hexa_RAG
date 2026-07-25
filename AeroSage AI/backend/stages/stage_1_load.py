import os
from pathlib import Path
from typing import List, TypedDict

FAA_DOCS_DIR = "data/faa_docs"
INCIDENT_REPORTS_DIR = "data/incident_reports"

ALLOWED_EXTENSIONS = (".txt", ".json")
FAA_ALLOWED_EXTENSIONS = (".txt", ".pdf")


class RawFile(TypedDict):
    filename: str
    content: str


class RawFaaFile(TypedDict, total=False):
    filename: str
    file_type: str  # "txt" or "pdf"
    raw_text: str  # present only when file_type == "txt"
    file_path: str  # present only when file_type == "pdf"


def _load_folder(folder_path: str) -> List[RawFile]:
    if not os.path.isdir(folder_path):
        return []

    files: List[RawFile] = []
    for entry in sorted(Path(folder_path).iterdir()):
        if entry.is_file() and entry.suffix.lower() in ALLOWED_EXTENSIONS:
            content = entry.read_text(encoding="utf-8")
            files.append({"filename": entry.name, "content": content})
    return files


def load_faa_docs() -> List[RawFaaFile]:
    if not os.path.isdir(FAA_DOCS_DIR):
        return []

    files: List[RawFaaFile] = []
    for entry in sorted(Path(FAA_DOCS_DIR).iterdir()):
        if not entry.is_file() or entry.suffix.lower() not in FAA_ALLOWED_EXTENSIONS:
            continue

        if entry.suffix.lower() == ".txt":
            files.append(
                {
                    "filename": entry.name,
                    "raw_text": entry.read_text(encoding="utf-8"),
                    "file_type": "txt",
                }
            )
        elif entry.suffix.lower() == ".pdf":
            # No read/decode here - PDFs are binary, and Docling (Stage 2)
            # needs a file path, not pre-read text.
            files.append(
                {
                    "filename": entry.name,
                    "file_path": str(entry),
                    "file_type": "pdf",
                }
            )
    return files


def load_incident_reports() -> List[RawFile]:
    return _load_folder(INCIDENT_REPORTS_DIR)
