<<<<<<< HEAD
"""
review_service.py - Çalışma ve SM-2 Algoritması Modülü

Review (çalışma) akışını ve SM-2 aralıklı tekrar algoritmasını yönetir.
Kartların due tarihlerini ve tekrar durumlarını hesaplar.
"""

import logging
from datetime import datetime, timedelta
from storage import (
    load_json, save_json, find_by_id, find_all_by_field,
    insert, update
)
from auth import get_current_user_id
from utils import get_today_str, add_days

logger = logging.getLogger(__name__)


def calculate_sm2(quality: int, repetition: int, ef: float, interval: int) -> tuple[int, float, int]:
    """
    SM-2 benzeri aralıklı tekrar algoritması.
    
    Args:
        quality: 0-5 arası kalite puanı
        repetition: Mevcut tekrar sayısı
        ef: Easiness Factor (başlangıç: 2.5)
        interval: Mevcut interval (gün)
    
    Returns:
        tuple: (new_repetition, new_ef, new_interval)
    """
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    if new_ef < 1.3:
        new_ef = 1.3
    
    if quality < 3:
        new_repetition = 0
        new_interval = 1
    else:
        new_repetition = repetition + 1
        
        if new_repetition == 1:
            new_interval = 1
        elif new_repetition == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)
    
    return new_repetition, round(new_ef, 2), new_interval


def get_due_cards(deck_id: int = None) -> tuple[bool, str, list]:
    """
    Bugün due olan kartları getirir.
    
    Args:
        deck_id: Belirli bir deck için filtrele (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Due kart listesi)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    today = get_today_str()
    
    srs_states = find_all_by_field('srs_state', 'user_id', user_id)
    
    due_srs = [s for s in srs_states if s.get('due_date', '') <= today]
    
    if not due_srs:
        return True, "Bugün çalışılacak kart yok. Tebrikler! 🎉", []
    
    cards = load_json('cards')
    decks = load_json('decks')
    
    user_deck_ids = [d['id'] for d in decks if d.get('user_id') == user_id]
    
    due_cards = []
    for srs in due_srs:
        card = next((c for c in cards if c['id'] == srs['card_id']), None)
        
        if not card:
            continue
        
        if card.get('deck_id') not in user_deck_ids:
            continue
        
        if deck_id and card.get('deck_id') != deck_id:
            continue
        
        card_info = card.copy()
        card_info['srs'] = {
            'due_date': srs.get('due_date'),
            'ef': srs.get('ef'),
            'repetition': srs.get('repetition'),
            'interval_days': srs.get('interval_days')
        }
        
        deck = next((d for d in decks if d['id'] == card.get('deck_id')), None)
        if deck:
            card_info['deck_name'] = deck.get('name', 'Bilinmeyen')
        
        due_cards.append(card_info)
    
    return True, f"Bugün {len(due_cards)} kart due.", due_cards


def submit_review(card_id: int, quality: int) -> tuple[bool, str, dict | None]:
    """
    Bir kartı çalışır ve review kaydeder.
    
    Args:
        card_id: Kart ID
        quality: 0-5 arası kalite puanı
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel SRS durumu veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    if not isinstance(quality, int) or quality < 0 or quality > 5:
        return False, "Kalite puanı 0-5 arasında olmalıdır.", None
    
    from card_service import get_card
    success, msg, card = get_card(card_id)
    if not success:
        return False, msg, None
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        srs = {
            'user_id': user_id,
            'card_id': card_id,
            'repetition': 0,
            'interval_days': 1,
            'ef': 2.5,
            'due_date': get_today_str(),
            'last_quality': None
        }
        srs = insert('srs_state', srs)
    
    old_rep = srs.get('repetition', 0)
    old_ef = srs.get('ef', 2.5)
    old_interval = srs.get('interval_days', 1)
    
    new_rep, new_ef, new_interval = calculate_sm2(quality, old_rep, old_ef, old_interval)
    
    new_due_date = add_days(get_today_str(), new_interval)
    
    updates = {
        'repetition': new_rep,
        'interval_days': new_interval,
        'ef': new_ef,
        'due_date': new_due_date,
        'last_quality': quality,
        'last_reviewed': datetime.now().isoformat()
    }
    
    updated_srs = update('srs_state', srs['id'], updates)
    
    review = {
        'user_id': user_id,
        'card_id': card_id,
        'quality': quality,
        'reviewed_at': datetime.now().isoformat()
    }
    insert('reviews', review)
    
    logger.info(f"Review kaydedildi: Card {card_id}, Quality {quality}, Due: {new_due_date}")
    
    return True, f"Güncellendi! Sonraki tekrar: {new_due_date}", updated_srs


def get_srs_state(card_id: int) -> tuple[bool, str, dict | None]:
    """
    Kartın SRS durumunu getirir.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, SRS durumu veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        return False, "Bu kart için SRS kaydı bulunamadı.", None
    
    return True, "SRS durumu bulundu.", srs


def reset_card(card_id: int) -> tuple[bool, str]:
    """
    Kartın SRS durumunu sıfırlar.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız."
    
    from card_service import get_card
    success, msg, card = get_card(card_id)
    if not success:
        return False, msg
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        return False, "Bu kart için SRS kaydı bulunamadı."
    
    updates = {
        'repetition': 0,
        'interval_days': 1,
        'ef': 2.5,
        'due_date': get_today_str(),
        'last_quality': None
    }
    
    update('srs_state', srs['id'], updates)
    logger.info(f"Kart SRS sıfırlandı: {card_id}")
    
    return True, "Kart başarıyla sıfırlandı!"
=======
"""
review_service.py - Çalışma ve SM-2 Algoritması Modülü

Review (çalışma) akışını ve SM-2 aralıklı tekrar algoritmasını yönetir.
Kartların due tarihlerini ve tekrar durumlarını hesaplar.
"""

import logging
from datetime import datetime, timedelta
from storage import (
    load_json, save_json, find_by_id, find_all_by_field,
    insert, update
)
from auth import get_current_user_id
from utils import get_today_str, add_days

logger = logging.getLogger(__name__)


def calculate_sm2(quality: int, repetition: int, ef: float, interval: int) -> tuple[int, float, int]:
    """
    SM-2 benzeri aralıklı tekrar algoritması.
    
    Args:
        quality: 0-5 arası kalite puanı
        repetition: Mevcut tekrar sayısı
        ef: Easiness Factor (başlangıç: 2.5)
        interval: Mevcut interval (gün)
    
    Returns:
        tuple: (new_repetition, new_ef, new_interval)
    """
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    if new_ef < 1.3:
        new_ef = 1.3
    
    if quality < 3:
        new_repetition = 0
        new_interval = 1
    else:
        new_repetition = repetition + 1
        
        if new_repetition == 1:
            new_interval = 1
        elif new_repetition == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)
    
    return new_repetition, round(new_ef, 2), new_interval


def get_due_cards(deck_id: int = None) -> tuple[bool, str, list]:
    """
    Bugün due olan kartları getirir.
    
    Args:
        deck_id: Belirli bir deck için filtrele (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Due kart listesi)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    today = get_today_str()
    
    srs_states = find_all_by_field('srs_state', 'user_id', user_id)
    
    due_srs = [s for s in srs_states if s.get('due_date', '') <= today]
    
    if not due_srs:
        return True, "Bugün çalışılacak kart yok. Tebrikler! 🎉", []
    
    cards = load_json('cards')
    decks = load_json('decks')
    
    user_deck_ids = [d['id'] for d in decks if d.get('user_id') == user_id]
    
    due_cards = []
    for srs in due_srs:
        card = next((c for c in cards if c['id'] == srs['card_id']), None)
        
        if not card:
            continue
        
        if card.get('deck_id') not in user_deck_ids:
            continue
        
        if deck_id and card.get('deck_id') != deck_id:
            continue
        
        card_info = card.copy()
        card_info['srs'] = {
            'due_date': srs.get('due_date'),
            'ef': srs.get('ef'),
            'repetition': srs.get('repetition'),
            'interval_days': srs.get('interval_days')
        }
        
        deck = next((d for d in decks if d['id'] == card.get('deck_id')), None)
        if deck:
            card_info['deck_name'] = deck.get('name', 'Bilinmeyen')
        
        due_cards.append(card_info)
    
    return True, f"Bugün {len(due_cards)} kart due.", due_cards


def submit_review(card_id: int, quality: int) -> tuple[bool, str, dict | None]:
    """
    Bir kartı çalışır ve review kaydeder.
    
    Args:
        card_id: Kart ID
        quality: 0-5 arası kalite puanı
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel SRS durumu veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    if not isinstance(quality, int) or quality < 0 or quality > 5:
        return False, "Kalite puanı 0-5 arasında olmalıdır.", None
    
    from card_service import get_card
    success, msg, card = get_card(card_id)
    if not success:
        return False, msg, None
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        srs = {
            'user_id': user_id,
            'card_id': card_id,
            'repetition': 0,
            'interval_days': 1,
            'ef': 2.5,
            'due_date': get_today_str(),
            'last_quality': None
        }
        srs = insert('srs_state', srs)
    
    old_rep = srs.get('repetition', 0)
    old_ef = srs.get('ef', 2.5)
    old_interval = srs.get('interval_days', 1)
    
    new_rep, new_ef, new_interval = calculate_sm2(quality, old_rep, old_ef, old_interval)
    
    new_due_date = add_days(get_today_str(), new_interval)
    
    updates = {
        'repetition': new_rep,
        'interval_days': new_interval,
        'ef': new_ef,
        'due_date': new_due_date,
        'last_quality': quality,
        'last_reviewed': datetime.now().isoformat()
    }
    
    updated_srs = update('srs_state', srs['id'], updates)
    
    review = {
        'user_id': user_id,
        'card_id': card_id,
        'quality': quality,
        'reviewed_at': datetime.now().isoformat()
    }
    insert('reviews', review)
    
    logger.info(f"Review kaydedildi: Card {card_id}, Quality {quality}, Due: {new_due_date}")
    
    return True, f"Güncellendi! Sonraki tekrar: {new_due_date}", updated_srs


def get_srs_state(card_id: int) -> tuple[bool, str, dict | None]:
    """
    Kartın SRS durumunu getirir.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, SRS durumu veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        return False, "Bu kart için SRS kaydı bulunamadı.", None
    
    return True, "SRS durumu bulundu.", srs


def reset_card(card_id: int) -> tuple[bool, str]:
    """
    Kartın SRS durumunu sıfırlar.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız."
    
    from card_service import get_card
    success, msg, card = get_card(card_id)
    if not success:
        return False, msg
    
    srs_states = load_json('srs_state')
    srs = next(
        (s for s in srs_states if s.get('card_id') == card_id and s.get('user_id') == user_id),
        None
    )
    
    if not srs:
        return False, "Bu kart için SRS kaydı bulunamadı."
    
    updates = {
        'repetition': 0,
        'interval_days': 1,
        'ef': 2.5,
        'due_date': get_today_str(),
        'last_quality': None
    }
    
    update('srs_state', srs['id'], updates)
    logger.info(f"Kart SRS sıfırlandı: {card_id}")
    
    return True, "Kart başarıyla sıfırlandı!"
>>>>>>> 49319f5dfc84fb8c02a88209b4cff51a53bda568
