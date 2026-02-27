import pytest

from app.services.idea_service import validate_attachment


def test_rejects_large_file():
    with pytest.raises(ValueError) as exc:
        validate_attachment("file.pdf", "application/pdf", 5 * 1024 * 1024 + 1)
    assert str(exc.value) == "file size exceeds 5MB limit"


def test_rejects_disallowed_type():
    with pytest.raises(ValueError) as exc:
        validate_attachment("file.exe", "application/octet-stream", 100)
    assert str(exc.value) == "file type not allowed"


def test_accepts_allowed_type():
    validate_attachment("file.pdf", "application/pdf", 100)
