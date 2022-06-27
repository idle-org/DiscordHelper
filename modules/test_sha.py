"""
Sha256 hash function.
"""

from hashlib import sha256
from modules import test_template, internal_io


def sha256_hash(path: str, cached_data: bytes = None) -> hex:
    """
    Returns the sha256 hash of the data.
    """
    if cached_data is None:
        with open(path, "rb") as f:
            return sha256(f.read()).hexdigest()
    return sha256(cached_data).hexdigest()


def sha256_hash_on_str(io_s: bytes) -> hex:
    """
    Returns the sha256 hash of the data.
    """
    return sha256(io_s).hexdigest()


class Sha256(test_template.TestWalkTemplateSimpleFunction):
    """
    Sha256 hash function.
    """
    def __init__(self, thread_parameters: internal_io.thread_parameters):
        """
        Sha256 hash function.
        """
        super().__init__(thread_parameters, sha256_hash, "", use_cache=True)
