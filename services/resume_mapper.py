"""
Maps each job role to its resume file on disk. Resumes are kept as
plain PDF files in the resumes/ folder rather than in the database,
since they rarely change and there's no real reason to store binary
files in SQLite.
"""

from pathlib import Path

from django.conf import settings

RESUME_DIR = Path(settings.BASE_DIR) / "resumes"

RESUME_MAP = {
    "frontend": "Sanket_lodhe_CV.pdf",
    "backend": "Sanket_lodhe_CV.pdf",
    "angular": "Sanket_lodhe_CV.pdf",
    "fullstack": "Sanket_lodhe_CV.pdf",
}

VALID_ROLES = list(RESUME_MAP.keys())


def get_resume_path(role: str) -> Path | None:
    """
    Returns the full path to the resume file for a given role.

    Returns None if the role isn't recognized, or if the role is
    recognized but the file is missing from disk. Callers should treat
    both cases the same way: there's no resume to send.
    """
    filename = RESUME_MAP.get(role)
    if filename is None:
        return None

    path = RESUME_DIR / filename
    if not path.exists():
        return None

    return path
