import hashlib
import os

def get_file_hash(path):
    """Oblicza hasz SHA-256 pliku."""
    if not os.path.exists(path) or os.path.isdir(path):
        return None
    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None
