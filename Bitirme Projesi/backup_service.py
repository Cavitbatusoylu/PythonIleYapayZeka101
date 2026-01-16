"""
backup_service.py - Yedekleme Servisi

Veri yedekleme ve geri yükleme işlemlerini yönetir.
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"


def create_backup() -> tuple[bool, str]:
    """
    Tüm veri klasörünü timestamp ile yedekler.
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    if not DATA_DIR.exists():
        return False, "Yedeklenecek veri bulunamadı."
    
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{timestamp}"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        shutil.copytree(DATA_DIR, backup_path)
        logger.info(f"Yedek oluşturuldu: {backup_path}")
        return True, f"Yedek oluşturuldu: {backup_name}"
    except Exception as e:
        logger.error(f"Yedekleme hatası: {e}")
        return False, f"Yedekleme hatası: {e}"


def list_backups() -> tuple[bool, str, list]:
    """
    Mevcut yedekleri listeler.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Yedek listesi)
    """
    if not BACKUP_DIR.exists():
        return True, "Henüz yedek oluşturulmamış.", []
    
    backups = []
    for item in sorted(BACKUP_DIR.iterdir(), reverse=True):
        if item.is_dir() and item.name.startswith("backup_"):
            size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            size_mb = round(size / (1024 * 1024), 2)
            
            backups.append({
                'name': item.name,
                'path': str(item),
                'size_mb': size_mb,
                'created': item.name.replace('backup_', '')
            })
    
    return True, f"{len(backups)} yedek bulundu.", backups


def restore_backup(backup_name: str) -> tuple[bool, str]:
    """
    Belirtilen yedeği geri yükler.
    
    Args:
        backup_name: Yedek adı
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    backup_path = BACKUP_DIR / backup_name
    
    if not backup_path.exists():
        return False, f"Yedek bulunamadı: {backup_name}"
    
    try:
        if DATA_DIR.exists():
            temp_backup = BACKUP_DIR / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(DATA_DIR, temp_backup)
            shutil.rmtree(DATA_DIR)
        
        shutil.copytree(backup_path, DATA_DIR)
        logger.info(f"Yedek geri yüklendi: {backup_name}")
        return True, f"Yedek başarıyla geri yüklendi: {backup_name}"
    except Exception as e:
        logger.error(f"Geri yükleme hatası: {e}")
        return False, f"Geri yükleme hatası: {e}"


def delete_backup(backup_name: str) -> tuple[bool, str]:
    """
    Belirtilen yedeği siler.
    
    Args:
        backup_name: Yedek adı
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    backup_path = BACKUP_DIR / backup_name
    
    if not backup_path.exists():
        return False, f"Yedek bulunamadı: {backup_name}"
    
    try:
        shutil.rmtree(backup_path)
        logger.info(f"Yedek silindi: {backup_name}")
        return True, f"Yedek silindi: {backup_name}"
    except Exception as e:
        logger.error(f"Yedek silme hatası: {e}")
        return False, f"Yedek silme hatası: {e}"


def export_to_csv(output_path: str = None) -> tuple[bool, str]:
    """
    Verileri CSV formatına dışa aktarır.
    
    Args:
        output_path: Çıktı dosya yolu (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    import csv
    import json
    
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = BACKUP_DIR / f"export_{timestamp}.csv"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(exist_ok=True)
    
    try:
        cards_file = DATA_DIR / "cards.json"
        if not cards_file.exists():
            return False, "Dışa aktarılacak kart bulunamadı."
        
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'deck_id', 'front', 'back', 'created_at'])
            
            for card in cards:
                writer.writerow([
                    card.get('id', ''),
                    card.get('deck_id', ''),
                    card.get('front', ''),
                    card.get('back', ''),
                    card.get('created_at', '')
                ])
        
        logger.info(f"CSV dışa aktarıldı: {output_path}")
        return True, f"CSV dışa aktarıldı: {output_path.name}"
    except Exception as e:
        logger.error(f"CSV dışa aktarma hatası: {e}")
        return False, f"CSV dışa aktarma hatası: {e}"


def import_from_csv(file_path: str, deck_id: int) -> tuple[bool, str, int]:
    """
    CSV dosyasından kartları içe aktarır.
    
    CSV formatı: front,back (ilk satır başlık olabilir)
    
    Args:
        file_path: CSV dosya yolu
        deck_id: Kartların ekleneceği deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Eklenen kart sayısı)
    """
    import csv
    from pathlib import Path
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"Dosya bulunamadı: {file_path}", 0
    
    if not file_path.suffix.lower() == '.csv':
        return False, "Sadece CSV dosyaları desteklenir.", 0
    
    try:
        from deck_service import get_deck
        success, msg, deck = get_deck(deck_id)
        if not success:
            return False, f"Geçersiz deck: {msg}", 0
        
        imported_count = 0
        from card_service import create_card
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            first_row = next(reader, None)
            if not first_row:
                return False, "CSV dosyası boş.", 0
            
            if first_row[0].lower() in ['front', 'soru', 'question', 'ön', 'on']:
                pass
            else:
                if len(first_row) >= 2:
                    success, _, _ = create_card(deck_id, first_row[0], first_row[1])
                    if success:
                        imported_count += 1
            
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    success, _, _ = create_card(deck_id, row[0].strip(), row[1].strip())
                    if success:
                        imported_count += 1
        
        logger.info(f"CSV import: {imported_count} kart eklendi (deck: {deck_id})")
        return True, f"{imported_count} kart başarıyla içe aktarıldı!", imported_count
    except Exception as e:
        logger.error(f"CSV içe aktarma hatası: {e}")
        return False, f"CSV içe aktarma hatası: {e}", 0

