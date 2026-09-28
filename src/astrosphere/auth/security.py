from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import struct
import time

from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime, timedelta, timezone


PASSWORD_RESET_MINUTES = 30
MFA_CODE_DIGITS = 6
MFA_STEP_SECONDS = 30


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_secure_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def password_reset_expiry() -> datetime:
    return utc_now() + timedelta(
        minutes=PASSWORD_RESET_MINUTES
    )


def generate_mfa_encryption_key() -> str:
    return Fernet.generate_key().decode("ascii")


def _get_mfa_fernet() -> Fernet:
    key = os.getenv("ASTROSPHERE_MFA_ENCRYPTION_KEY", "").strip()

    if not key:
        raise RuntimeError(
            "ASTROSPHERE_MFA_ENCRYPTION_KEY is not configured."
        )

    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "ASTROSPHERE_MFA_ENCRYPTION_KEY is invalid."
        ) from exc


def encrypt_mfa_secret(secret: str) -> str:
    if not secret:
        raise ValueError("MFA secret is required.")

    encrypted = _get_mfa_fernet().encrypt(
        secret.encode("utf-8")
    )

    return encrypted.decode("ascii")


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    if not encrypted_secret:
        raise ValueError("Encrypted MFA secret is required.")

    try:
        decrypted = _get_mfa_fernet().decrypt(
            encrypted_secret.encode("ascii")
        )
    except (InvalidToken, ValueError, TypeError) as exc:
        raise ValueError(
            "Unable to decrypt MFA secret."
        ) from exc

    return decrypted.decode("utf-8")

def generate_mfa_secret() -> str:
    secret = secrets.token_bytes(20)

    return base64.b32encode(
        secret
    ).decode("ascii").rstrip("=")


def _decode_base32_secret(secret: str) -> bytes:
    padding = "=" * (
        (-len(secret)) % 8
    )

    return base64.b32decode(
        secret + padding,
        casefold=True,
    )


def generate_totp_code(
    secret: str,
    timestamp: int | None = None,
) -> str:
    if timestamp is None:
        timestamp = int(time.time())

    counter = timestamp // MFA_STEP_SECONDS

    key = _decode_base32_secret(secret)

    message = struct.pack(
        ">Q",
        counter,
    )

    digest = hmac.new(
        key,
        message,
        hashlib.sha1,
    ).digest()

    offset = digest[-1] & 0x0F

    binary_code = (
        ((digest[offset] & 0x7F) << 24)
        | (digest[offset + 1] << 16)
        | (digest[offset + 2] << 8)
        | digest[offset + 3]
    )

    code = binary_code % (
        10 ** MFA_CODE_DIGITS
    )

    return f"{code:0{MFA_CODE_DIGITS}d}"


def verify_totp_code(
    secret: str,
    code: str,
    timestamp: int | None = None,
) -> bool:
    if timestamp is None:
        timestamp = int(time.time())

    supplied = code.strip()

    if len(supplied) != MFA_CODE_DIGITS:
        return False

    if not supplied.isdigit():
        return False

    # Allow the current 30-second window and one
    # adjacent window in either direction to account
    # for small clock differences.
    for offset in (-1, 0, 1):
        candidate = generate_totp_code(
            secret,
            timestamp=timestamp + (
                offset * MFA_STEP_SECONDS
            ),
        )

        if hmac.compare_digest(
            candidate,
            supplied,
        ):
            return True

    return False


def build_totp_uri(
    secret: str,
    username: str,
    issuer: str = "AstroSphere",
) -> str:
    from urllib.parse import quote

    label = f"{issuer}:{username}"

    return (
        "otpauth://totp/"
        f"{quote(label)}"
        f"?secret={quote(secret)}"
        f"&issuer={quote(issuer)}"
        f"&algorithm=SHA1"
        f"&digits={MFA_CODE_DIGITS}"
        f"&period={MFA_STEP_SECONDS}"
    )


def generate_recovery_codes(
    count: int = 10,
) -> list[str]:
    codes = []

    for _ in range(count):
        part_a = secrets.token_hex(4).upper()
        part_b = secrets.token_hex(4).upper()

        codes.append(
            f"{part_a}-{part_b}"
        )

    return codes


def hash_recovery_code(code: str) -> str:
    return hashlib.sha256(
        code.strip().upper().encode("utf-8")
    ).hexdigest()
