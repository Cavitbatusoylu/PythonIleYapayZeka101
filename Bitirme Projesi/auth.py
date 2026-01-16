"""
auth.py - Kimlik Doğrulama Modülü

Kullanıcı kayıt, giriş, çıkış ve parola hashleme işlemlerini yönetir.
Güvenli parola saklama için PBKDF2 + salt kullanır.
"""

import os
import hashlib
import logging
from storage import load_json, save_json, get_next_id, find_by_field, insert
from utils import validate_email, validate_password

logger = logging.getLogger(__name__)

_current_session = {
    'user_id': None,
    'email': None,
    'logged_in': False
}


def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """
    Parolayı PBKDF2-HMAC-SHA256 ile hashler.
    
    Args:
        password: Ham parola
        salt: Tuz (opsiyonel, yoksa yeni üretilir)
    
    Returns:
        tuple: (password_hash, salt) - hex string olarak
    """
    if salt is None:
        salt = os.urandom(32)  # 256-bit salt
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=100000  # 100k iterasyon
    )
    
    return password_hash.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """
    Parolayı doğrular.
    
    Args:
        password: Kontrol edilecek parola
        stored_hash: Saklanan hash (hex)
        stored_salt: Saklanan salt (hex)
    
    Returns:
        bool: Parola doğru ise True
    """
    try:
        salt = bytes.fromhex(stored_salt)
        computed_hash, _ = hash_password(password, salt)
        return computed_hash == stored_hash
    except Exception as e:
        logger.error(f"Parola doğrulama hatası: {e}")
        return False


def register(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Yeni kullanıcı kaydı oluşturur.
    
    Args:
        email: E-posta adresi
        password: Parola
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kullanıcı verisi veya None)
    """
    if not validate_email(email):
        return False, "Geçersiz e-posta formatı.", None
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg, None
    
    existing_user = find_by_field('users', 'email', email)
    if existing_user:
        logger.warning(f"Kayıt denemesi - email zaten mevcut: {email}")
        return False, "Bu e-posta adresi zaten kayıtlı.", None
    
    password_hash, salt = hash_password(password)
    
    user = {
        'email': email,
        'password_hash': password_hash,
        'salt': salt,
        'created_at': get_current_datetime()
    }
    
    saved_user = insert('users', user)
    
    logger.info(f"Yeni kullanıcı kaydı: {email} (ID: {saved_user['id']})")
    
    safe_user = {k: v for k, v in saved_user.items() if k not in ['password_hash', 'salt']}
    
    return True, "Kayıt başarılı!", safe_user


def login(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Kullanıcı girişi yapar.
    
    Args:
        email: E-posta adresi
        password: Parola
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kullanıcı verisi veya None)
    """
    global _current_session
    
    if _current_session['logged_in']:
        return False, "Zaten giriş yapılmış. Önce çıkış yapın.", None
    
    user = find_by_field('users', 'email', email)
    if not user:
        logger.warning(f"Başarısız giriş denemesi - kullanıcı bulunamadı: {email}")
        return False, "E-posta veya parola hatalı.", None
    
    if not verify_password(password, user['password_hash'], user['salt']):
        logger.warning(f"Başarısız giriş denemesi - yanlış parola: {email}")
        return False, "E-posta veya parola hatalı.", None
    
    _current_session['user_id'] = user['id']
    _current_session['email'] = user['email']
    _current_session['logged_in'] = True
    
    logger.info(f"Kullanıcı girişi başarılı: {email} (ID: {user['id']})")
    
    safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
    
    return True, f"Hoş geldiniz, {email}!", safe_user


def logout() -> tuple[bool, str]:
    """
    Oturumu kapatır.
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    global _current_session
    
    if not _current_session['logged_in']:
        return False, "Zaten giriş yapılmamış."
    
    email = _current_session['email']
    
    _current_session['user_id'] = None
    _current_session['email'] = None
    _current_session['logged_in'] = False
    
    logger.info(f"Kullanıcı çıkışı: {email}")
    
    return True, "Çıkış yapıldı. Güle güle!"


def get_current_user() -> dict | None:
    """
    Mevcut oturumdaki kullanıcıyı döndürür.
    
    Returns:
        dict | None: Kullanıcı verisi veya None
    """
    if not _current_session['logged_in']:
        return None
    
    return {
        'id': _current_session['user_id'],
        'email': _current_session['email']
    }


def get_current_user_id() -> int | None:
    """
    Mevcut kullanıcının ID'sini döndürür.
    
    Returns:
        int | None: Kullanıcı ID veya None
    """
    if not _current_session['logged_in']:
        return None
    return _current_session['user_id']


def is_logged_in() -> bool:
    """
    Oturum açık mı kontrol eder.
    
    Returns:
        bool: Oturum açık ise True
    """
    return _current_session['logged_in']


def require_login(func):
    """
    Decorator: Fonksiyonun çalışması için giriş yapılmış olmasını gerektirir.
    """
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return False, "Bu işlem için giriş yapmalısınız.", None
        return func(*args, **kwargs)
    return wrapper


def get_current_datetime() -> str:
    """
    Şu anki tarih/saati ISO formatında döndürür.
    
    Returns:
        str: ISO format datetime
    """
    from datetime import datetime
    return datetime.now().isoformat()
