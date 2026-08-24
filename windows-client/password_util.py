"""
Password Util - Kiểm tra mật khẩu emergency unlock.

Mật khẩu được lưu dạng SHA-256 hash trong config.py. Vẫn hỗ trợ cấu hình cũ
dùng plaintext (EMERGENCY_UNLOCK_PASSWORD) để không phá vỡ cài đặt sẵn có.
"""

import hashlib
import hmac

# Hash của "admin123" - dùng để cảnh báo khi người dùng chưa đổi mật khẩu
DEFAULT_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"


def hash_password(password):
    """Trả về SHA-256 hex digest của mật khẩu"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _get_config():
    """Đọc cấu hình mật khẩu, chấp nhận thiếu key (cấu hình cũ)"""
    import config
    return (
        getattr(config, "EMERGENCY_UNLOCK_PASSWORD_HASH", "") or "",
        getattr(config, "EMERGENCY_UNLOCK_PASSWORD", "") or "",
    )


def verify_password(password):
    """
    So khớp mật khẩu người dùng nhập với cấu hình.
    Ưu tiên hash; nếu chưa cấu hình hash thì so plaintext.
    """
    configured_hash, plaintext = _get_config()

    if configured_hash:
        return hmac.compare_digest(hash_password(password), configured_hash.lower())

    if plaintext:
        return hmac.compare_digest(password, plaintext)

    # Không cấu hình gì cả -> từ chối, tránh mở khóa bằng chuỗi rỗng
    print("⚠️ Chưa cấu hình mật khẩu emergency unlock trong config.py")
    return False


def is_default_password():
    """True nếu mật khẩu vẫn là 'admin123' mặc định"""
    configured_hash, plaintext = _get_config()

    if configured_hash:
        return configured_hash.lower() == DEFAULT_PASSWORD_HASH
    return plaintext == "admin123"
