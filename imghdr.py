"""
Lightweight fallback implementation of the stdlib `imghdr.what` used by
Streamlit. Some hosted Python environments may not expose the stdlib
`imghdr` module; adding this file to the repo allows Streamlit to import
`imghdr` from the project root.

This implementation:
- tries to use Pillow (PIL) if available for robust format detection,
- otherwise falls back to simple header checks for common formats.

It only implements the minimal `what(filename, h=None)` signature used by
Streamlit to determine image type.
"""
from __future__ import annotations

from typing import Optional

try:
    from PIL import Image
    from io import BytesIO
except Exception:
    Image = None
    BytesIO = None


def what(file: str | bytes | None, h: bytes | None = None) -> Optional[str]:
    """Return a string describing the image type or None.

    Parameters
    - file: path to file, or bytes (if h is None, file should be a path)
    - h: optional header bytes

    This mirrors the stdlib `imghdr.what` minimal behaviour used by
    third-party libraries.
    """
    data = h

    # If header bytes weren't provided, try to read a small chunk from file
    if data is None:
        try:
            # if file is bytes-like, use it directly
            if isinstance(file, (bytes, bytearray)):
                data = bytes(file)[:32]
            else:
                with open(str(file), "rb") as f:
                    data = f.read(32)
        except Exception:
            return None

    # If Pillow is available, prefer it
    if Image and BytesIO:
        try:
            img = Image.open(BytesIO(data))
            fmt = img.format
            if fmt:
                return fmt.lower()
        except Exception:
            # fall back to header checks
            pass

    # Basic header checks for common image types
    if not data:
        return None

    if data.startswith(b"\xff\xd8"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data.startswith(b"BM"):
        return "bmp"
    # TIFF ('II' or 'MM' + magic)
    if data.startswith(b"II") or data.startswith(b"MM"):
        return "tiff"

    return None
