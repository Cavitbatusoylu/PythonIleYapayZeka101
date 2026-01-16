"""
storage.py - Veri Erişim Katmanı

JSON dosyalarını okuma/yazma, atomic write ve ID üretimi işlemlerini yapar.
Tüm veri işlemleri bu modül üzerinden gerçekleştirilir.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('studybuddy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"

FILES = {
    'users': 'users.json',
    'decks': 'decks.json',
    'cards': 'cards.json',
    'srs_state': 'srs_state.json',
    'reviews': 'reviews.json'
}


def ensure_data_dir():
    """
    data/ klasörünün var olduğundan emin olur.
    Yoksa oluşturur.
    """
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
        logger.info(f"Veri klasörü oluşturuldu: {DATA_DIR}")


def get_file_path(collection_name: str) -> Path:
    """
    Koleksiyon adına göre dosya yolunu döndürür.
    
    Args:
        collection_name: Koleksiyon adı (users, decks, cards, srs_state, reviews)
    
    Returns:
        Path: Dosya yolu
    """
    if collection_name not in FILES:
        raise ValueError(f"Bilinmeyen koleksiyon: {collection_name}")
    return DATA_DIR / FILES[collection_name]


def load_json(collection_name: str) -> list:
    """
    JSON dosyasını okur ve liste olarak döndürür.
    Dosya yoksa boş liste döndürür.
    
    Args:
        collection_name: Koleksiyon adı
    
    Returns:
        list: Veri listesi
    """
    ensure_data_dir()
    file_path = get_file_path(collection_name)
    
    if not file_path.exists():
        logger.debug(f"Dosya bulunamadı, boş liste döndürülüyor: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"{collection_name} yüklendi: {len(data)} kayıt")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON okuma hatası ({file_path}): {e}")
        return []


def save_json(collection_name: str, data: list) -> bool:
    """
    Veriyi JSON dosyasına atomic write ile kaydeder.
    Önce geçici dosyaya yazar, sonra asıl dosyanın üstüne geçer.
    
    Args:
        collection_name: Koleksiyon adı
        data: Kaydedilecek veri listesi
    
    Returns:
        bool: Başarılı ise True
    """
    ensure_data_dir()
    file_path = get_file_path(collection_name)
    temp_path = file_path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        os.replace(temp_path, file_path)
        logger.info(f"{collection_name} kaydedildi: {len(data)} kayıt")
        return True
    except Exception as e:
        logger.error(f"Kaydetme hatası ({file_path}): {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def generate_id() -> int:
    """
    Benzersiz ID üretir (UUID tabanlı, integer'a çevrilmiş).
    
    Returns:
        int: Benzersiz ID
    """
    return int(uuid.uuid4().hex[:8], 16)


def get_next_id(collection_name: str) -> int:
    """
    Koleksiyon için bir sonraki ID'yi döndürür.
    Mevcut en yüksek ID + 1 veya 1 döner.
    
    Args:
        collection_name: Koleksiyon adı
    
    Returns:
        int: Sonraki ID
    """
    data = load_json(collection_name)
    if not data:
        return 1
    
    max_id = max(item.get('id', 0) for item in data)
    return max_id + 1


def find_by_id(collection_name: str, item_id: int) -> dict | None:
    """
    ID'ye göre kayıt bulur.
    
    Args:
        collection_name: Koleksiyon adı
        item_id: Aranacak ID
    
    Returns:
        dict | None: Bulunan kayıt veya None
    """
    data = load_json(collection_name)
    for item in data:
        if item.get('id') == item_id:
            return item
    return None


def find_by_field(collection_name: str, field: str, value) -> dict | None:
    """
    Belirli bir alana göre kayıt bulur.
    
    Args:
        collection_name: Koleksiyon adı
        field: Alan adı
        value: Aranacak değer
    
    Returns:
        dict | None: Bulunan ilk kayıt veya None
    """
    data = load_json(collection_name)
    for item in data:
        if item.get(field) == value:
            return item
    return None


def find_all_by_field(collection_name: str, field: str, value) -> list:
    """
    Belirli bir alana göre tüm kayıtları bulur.
    
    Args:
        collection_name: Koleksiyon adı
        field: Alan adı
        value: Aranacak değer
    
    Returns:
        list: Bulunan kayıtlar
    """
    data = load_json(collection_name)
    return [item for item in data if item.get(field) == value]


def insert(collection_name: str, item: dict) -> dict:
    """
    Yeni kayıt ekler.
    
    Args:
        collection_name: Koleksiyon adı
        item: Eklenecek kayıt (id otomatik atanır)
    
    Returns:
        dict: Eklenen kayıt (id ile birlikte)
    """
    data = load_json(collection_name)
    
    if 'id' not in item:
        item['id'] = get_next_id(collection_name)
    
    if 'created_at' not in item:
        item['created_at'] = datetime.now().isoformat()
    
    data.append(item)
    save_json(collection_name, data)
    
    logger.info(f"Yeni kayıt eklendi: {collection_name} #{item['id']}")
    return item


def update(collection_name: str, item_id: int, updates: dict) -> dict | None:
    """
    Mevcut kaydı günceller.
    
    Args:
        collection_name: Koleksiyon adı
        item_id: Güncellenecek kayıt ID'si
        updates: Güncellenecek alanlar
    
    Returns:
        dict | None: Güncellenen kayıt veya None
    """
    data = load_json(collection_name)
    
    for i, item in enumerate(data):
        if item.get('id') == item_id:
            data[i].update(updates)
            data[i]['updated_at'] = datetime.now().isoformat()
            save_json(collection_name, data)
            logger.info(f"Kayıt güncellendi: {collection_name} #{item_id}")
            return data[i]
    
    logger.warning(f"Güncellenecek kayıt bulunamadı: {collection_name} #{item_id}")
    return None


def delete(collection_name: str, item_id: int) -> bool:
    """
    Kaydı siler.
    
    Args:
        collection_name: Koleksiyon adı
        item_id: Silinecek kayıt ID'si
    
    Returns:
        bool: Başarılı ise True
    """
    data = load_json(collection_name)
    original_length = len(data)
    
    data = [item for item in data if item.get('id') != item_id]
    
    if len(data) < original_length:
        save_json(collection_name, data)
        logger.info(f"Kayıt silindi: {collection_name} #{item_id}")
        return True
    
    logger.warning(f"Silinecek kayıt bulunamadı: {collection_name} #{item_id}")
    return False


def delete_by_field(collection_name: str, field: str, value) -> int:
    """
    Belirli bir alana göre tüm kayıtları siler.
    
    Args:
        collection_name: Koleksiyon adı
        field: Alan adı
        value: Silinecek değer
    
    Returns:
        int: Silinen kayıt sayısı
    """
    data = load_json(collection_name)
    original_length = len(data)
    
    data = [item for item in data if item.get(field) != value]
    deleted_count = original_length - len(data)
    
    if deleted_count > 0:
        save_json(collection_name, data)
        logger.info(f"{deleted_count} kayıt silindi: {collection_name} ({field}={value})")
    
    return deleted_count


def get_current_datetime() -> str:
    """
    Şu anki tarih/saati ISO formatında döndürür.
    
    Returns:
        str: ISO format datetime
    """
    return datetime.now().isoformat()


def get_current_date() -> str:
    """
    Şu anki tarihi YYYY-MM-DD formatında döndürür.
    
    Returns:
        str: YYYY-MM-DD format tarih
    """
    return datetime.now().strftime('%Y-%m-%d')


ensure_data_dir()
