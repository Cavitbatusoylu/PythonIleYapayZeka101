"""
utils.py - Yardımcı Fonksiyonlar

Tarih işlemleri, input doğrulama ve genel yardımcı fonksiyonlar.
"""

import re
from datetime import datetime, timedelta


def validate_email(email: str) -> bool:
    """
    E-posta adresinin geçerli formatı kontrol eder.
    
    Args:
        email: Kontrol edilecek e-posta
    
    Returns:
        bool: Geçerli ise True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Parolanın güvenlik kurallarına uygun olup olmadığını kontrol eder.
    
    Args:
        password: Kontrol edilecek parola
    
    Returns:
        tuple: (Geçerli mi, Hata mesajı)
    """
    if len(password) < 6:
        return False, "Parola en az 6 karakter olmalıdır."
    
    return True, ""


def parse_date(date_str: str) -> datetime | None:
    """
    Tarih string'ini datetime objesine çevirir.
    
    Args:
        date_str: YYYY-MM-DD formatında tarih
    
    Returns:
        datetime | None: Tarih objesi veya None
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def format_date(dt: datetime) -> str:
    """
    Datetime objesini YYYY-MM-DD formatına çevirir.
    
    Args:
        dt: Datetime objesi
    
    Returns:
        str: YYYY-MM-DD formatında tarih
    """
    return dt.strftime('%Y-%m-%d')


def get_today() -> datetime:
    """
    Bugünün tarihini döndürür (saat bilgisi olmadan).
    
    Returns:
        datetime: Bugünün tarihi
    """
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def get_today_str() -> str:
    """
    Bugünün tarihini string olarak döndürür.
    
    Returns:
        str: YYYY-MM-DD formatında bugün
    """
    return format_date(get_today())


def add_days(date_str: str, days: int) -> str:
    """
    Tarihe gün ekler.
    
    Args:
        date_str: YYYY-MM-DD formatında başlangıç tarihi
        days: Eklenecek gün sayısı
    
    Returns:
        str: YYYY-MM-DD formatında yeni tarih
    """
    dt = parse_date(date_str)
    if dt is None:
        dt = get_today()
    
    new_dt = dt + timedelta(days=days)
    return format_date(new_dt)


def is_due(due_date_str: str) -> bool:
    """
    Kartın bugün due olup olmadığını kontrol eder.
    
    Args:
        due_date_str: YYYY-MM-DD formatında due tarihi
    
    Returns:
        bool: Due ise True
    """
    due_date = parse_date(due_date_str)
    if due_date is None:
        return True  # Tarih geçersizse due say
    
    return due_date <= get_today()


def get_quality_description(quality: int) -> str:
    """
    Kalite puanının açıklamasını döndürür.
    
    Args:
        quality: 0-5 arası kalite puanı
    
    Returns:
        str: Puan açıklaması
    """
    descriptions = {
        0: "Hiç hatırlamadım",
        1: "Çok zor hatırladım",
        2: "Kısmen hatırladım",
        3: "Doğru ama zor",
        4: "Doğru ve rahat",
        5: "Mükemmel / akıcı"
    }
    return descriptions.get(quality, "Bilinmeyen puan")


def get_input(prompt: str, validator=None, error_msg: str = "Geçersiz giriş.") -> str:
    """
    Kullanıcıdan doğrulanmış input alır.
    
    Args:
        prompt: Kullanıcıya gösterilecek mesaj
        validator: Doğrulama fonksiyonu (opsiyonel)
        error_msg: Hata mesajı
    
    Returns:
        str: Kullanıcı girişi
    """
    while True:
        value = input(prompt).strip()
        
        if validator is None:
            return value
        
        if validator(value):
            return value
        
        print(f"❌ {error_msg}")


def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """
    Kullanıcıdan integer input alır.
    
    Args:
        prompt: Kullanıcıya gösterilecek mesaj
        min_val: Minimum değer (opsiyonel)
        max_val: Maximum değer (opsiyonel)
    
    Returns:
        int: Kullanıcı girişi
    """
    while True:
        try:
            value = int(input(prompt).strip())
            
            if min_val is not None and value < min_val:
                print(f"❌ Değer en az {min_val} olmalıdır.")
                continue
            
            if max_val is not None and value > max_val:
                print(f"❌ Değer en fazla {max_val} olmalıdır.")
                continue
            
            return value
        except ValueError:
            print("❌ Lütfen geçerli bir sayı girin.")


def confirm(prompt: str) -> bool:
    """
    Kullanıcıdan onay alır.
    
    Args:
        prompt: Kullanıcıya gösterilecek mesaj
    
    Returns:
        bool: Onay verildiyse True
    """
    response = input(f"{prompt} (E/H): ").strip().lower()
    return response in ['e', 'evet', 'y', 'yes']


def clear_screen():
    """
    Ekranı temizler (opsiyonel, platforma bağlı).
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """
    Başlık yazdırır.
    
    Args:
        title: Başlık metni
    """
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_success(message: str):
    """
    Başarı mesajı yazdırır.
    
    Args:
        message: Mesaj
    """
    print(f"✅ {message}")


def print_error(message: str):
    """
    Hata mesajı yazdırır.
    
    Args:
        message: Mesaj
    """
    print(f"❌ {message}")


def print_warning(message: str):
    """
    Uyarı mesajı yazdırır.
    
    Args:
        message: Mesaj
    """
    print(f"⚠️ {message}")


def print_info(message: str):
    """
    Bilgi mesajı yazdırır.
    
    Args:
        message: Mesaj
    """
    print(f"ℹ️ {message}")
