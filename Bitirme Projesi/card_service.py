<<<<<<< HEAD
"""
card_service.py - Kart Yönetimi Modülü

Flashcard (kart) CRUD işlemlerini yönetir.
Her kart bir deck'e aittir ve front/back alanlarına sahiptir.
"""

import logging
from storage import (
    load_json, find_by_id, find_all_by_field,
    insert, update, delete, delete_by_field
)
from auth import get_current_user_id
from deck_service import get_deck
from utils import get_today_str

logger = logging.getLogger(__name__)


def create_card(deck_id: int, front: str, back: str) -> tuple[bool, str, dict | None]:
    """
    Yeni kart oluşturur ve SRS state'ini başlatır.
    
    Args:
        deck_id: Kartın ekleneceği deck ID
        front: Ön yüz (soru)
        back: Arka yüz (cevap)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    success, msg, deck = get_deck(deck_id)
    if not success:
        return False, f"Geçersiz deck: {msg}", None
    
    if not front or not front.strip():
        return False, "Kart ön yüzü (soru) boş olamaz.", None
    
    if not back or not back.strip():
        return False, "Kart arka yüzü (cevap) boş olamaz.", None
    
    card = {
        'deck_id': deck_id,
        'front': front.strip(),
        'back': back.strip()
    }
    
    saved_card = insert('cards', card)
    
    srs_state = {
        'user_id': user_id,
        'card_id': saved_card['id'],
        'repetition': 0,
        'interval_days': 1,
        'ef': 2.5,  # Başlangıç EF
        'due_date': get_today_str(),  # Hemen due
        'last_quality': None
    }
    
    insert('srs_state', srs_state)
    
    logger.info(f"Kart oluşturuldu: {saved_card['id']} (Deck: {deck_id})")
    
    return True, "Kart başarıyla eklendi!", saved_card


def list_cards(deck_id: int) -> tuple[bool, str, list]:
    """
    Deck'in tüm kartlarını listeler.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart listesi)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return False, msg, []
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    
    user_id = get_current_user_id()
    srs_states = load_json('srs_state')
    
    for card in cards:
        card_srs = next(
            (s for s in srs_states if s.get('card_id') == card['id'] and s.get('user_id') == user_id),
            None
        )
        if card_srs:
            card['due_date'] = card_srs.get('due_date')
            card['ef'] = card_srs.get('ef')
            card['repetition'] = card_srs.get('repetition')
    
    return True, f"{len(cards)} kart bulundu.", cards


def get_card(card_id: int) -> tuple[bool, str, dict | None]:
    """
    ID'ye göre kart getirir.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    card = find_by_id('cards', card_id)
    
    if not card:
        return False, "Kart bulunamadı.", None
    
    success, msg, deck = get_deck(card['deck_id'])
    if not success:
        logger.warning(f"Yetkisiz kart erişimi: User {user_id} -> Card {card_id}")
        return False, "Bu karta erişim izniniz yok.", None
    
    return True, "Kart bulundu.", card


def update_card(card_id: int, front: str = None, back: str = None) -> tuple[bool, str, dict | None]:
    """
    Kart bilgilerini günceller.
    
    Args:
        card_id: Kart ID
        front: Yeni ön yüz (opsiyonel)
        back: Yeni arka yüz (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel kart verisi veya None)
    """
    success, msg, card = get_card(card_id)
    if not success:
        return success, msg, None
    
    updates = {}
    
    if front is not None:
        if not front.strip():
            return False, "Kart ön yüzü boş olamaz.", None
        updates['front'] = front.strip()
    
    if back is not None:
        if not back.strip():
            return False, "Kart arka yüzü boş olamaz.", None
        updates['back'] = back.strip()
    
    if not updates:
        return False, "Güncellenecek bir alan belirtilmedi.", None
    
    updated_card = update('cards', card_id, updates)
    
    if updated_card:
        logger.info(f"Kart güncellendi: {card_id}")
        return True, "Kart başarıyla güncellendi!", updated_card
    
    return False, "Kart güncellenirken bir hata oluştu.", None


def delete_card(card_id: int) -> tuple[bool, str]:
    """
    Kartı ve SRS state'ini siler.
    
    Args:
        card_id: Silinecek kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    success, msg, card = get_card(card_id)
    if not success:
        return success, msg
    
    delete_by_field('srs_state', 'card_id', card_id)
    delete_by_field('reviews', 'card_id', card_id)
    
    if delete('cards', card_id):
        logger.info(f"Kart silindi: {card_id}")
        return True, "Kart başarıyla silindi!"
    
    return False, "Kart silinirken bir hata oluştu."


def search_cards(query: str, deck_id: int = None) -> tuple[bool, str, list]:
    """
    Kartlarda arama yapar.
    
    Args:
        query: Arama sorgusu
        deck_id: Belirli bir deck'te arama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Bulunan kartlar)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    from deck_service import list_decks
    _, _, user_decks = list_decks()
    user_deck_ids = [d['id'] for d in user_decks]
    
    all_cards = load_json('cards')
    query_lower = query.lower()
    
    results = []
    for card in all_cards:
        if card.get('deck_id') not in user_deck_ids:
            continue
        
        if deck_id and card.get('deck_id') != deck_id:
            continue
        
        if query_lower in card.get('front', '').lower() or query_lower in card.get('back', '').lower():
            results.append(card)
    
    return True, f"{len(results)} kart bulundu.", results
=======
"""
card_service.py - Kart Yönetimi Modülü

Flashcard (kart) CRUD işlemlerini yönetir.
Her kart bir deck'e aittir ve front/back alanlarına sahiptir.
"""

import logging
from storage import (
    load_json, find_by_id, find_all_by_field,
    insert, update, delete, delete_by_field
)
from auth import get_current_user_id
from deck_service import get_deck
from utils import get_today_str

logger = logging.getLogger(__name__)


def create_card(deck_id: int, front: str, back: str) -> tuple[bool, str, dict | None]:
    """
    Yeni kart oluşturur ve SRS state'ini başlatır.
    
    Args:
        deck_id: Kartın ekleneceği deck ID
        front: Ön yüz (soru)
        back: Arka yüz (cevap)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    success, msg, deck = get_deck(deck_id)
    if not success:
        return False, f"Geçersiz deck: {msg}", None
    
    if not front or not front.strip():
        return False, "Kart ön yüzü (soru) boş olamaz.", None
    
    if not back or not back.strip():
        return False, "Kart arka yüzü (cevap) boş olamaz.", None
    
    card = {
        'deck_id': deck_id,
        'front': front.strip(),
        'back': back.strip()
    }
    
    saved_card = insert('cards', card)
    
    srs_state = {
        'user_id': user_id,
        'card_id': saved_card['id'],
        'repetition': 0,
        'interval_days': 1,
        'ef': 2.5,  # Başlangıç EF
        'due_date': get_today_str(),  # Hemen due
        'last_quality': None
    }
    
    insert('srs_state', srs_state)
    
    logger.info(f"Kart oluşturuldu: {saved_card['id']} (Deck: {deck_id})")
    
    return True, "Kart başarıyla eklendi!", saved_card


def list_cards(deck_id: int) -> tuple[bool, str, list]:
    """
    Deck'in tüm kartlarını listeler.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart listesi)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return False, msg, []
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    
    user_id = get_current_user_id()
    srs_states = load_json('srs_state')
    
    for card in cards:
        card_srs = next(
            (s for s in srs_states if s.get('card_id') == card['id'] and s.get('user_id') == user_id),
            None
        )
        if card_srs:
            card['due_date'] = card_srs.get('due_date')
            card['ef'] = card_srs.get('ef')
            card['repetition'] = card_srs.get('repetition')
    
    return True, f"{len(cards)} kart bulundu.", cards


def get_card(card_id: int) -> tuple[bool, str, dict | None]:
    """
    ID'ye göre kart getirir.
    
    Args:
        card_id: Kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Kart verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    card = find_by_id('cards', card_id)
    
    if not card:
        return False, "Kart bulunamadı.", None
    
    success, msg, deck = get_deck(card['deck_id'])
    if not success:
        logger.warning(f"Yetkisiz kart erişimi: User {user_id} -> Card {card_id}")
        return False, "Bu karta erişim izniniz yok.", None
    
    return True, "Kart bulundu.", card


def update_card(card_id: int, front: str = None, back: str = None) -> tuple[bool, str, dict | None]:
    """
    Kart bilgilerini günceller.
    
    Args:
        card_id: Kart ID
        front: Yeni ön yüz (opsiyonel)
        back: Yeni arka yüz (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel kart verisi veya None)
    """
    success, msg, card = get_card(card_id)
    if not success:
        return success, msg, None
    
    updates = {}
    
    if front is not None:
        if not front.strip():
            return False, "Kart ön yüzü boş olamaz.", None
        updates['front'] = front.strip()
    
    if back is not None:
        if not back.strip():
            return False, "Kart arka yüzü boş olamaz.", None
        updates['back'] = back.strip()
    
    if not updates:
        return False, "Güncellenecek bir alan belirtilmedi.", None
    
    updated_card = update('cards', card_id, updates)
    
    if updated_card:
        logger.info(f"Kart güncellendi: {card_id}")
        return True, "Kart başarıyla güncellendi!", updated_card
    
    return False, "Kart güncellenirken bir hata oluştu.", None


def delete_card(card_id: int) -> tuple[bool, str]:
    """
    Kartı ve SRS state'ini siler.
    
    Args:
        card_id: Silinecek kart ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    success, msg, card = get_card(card_id)
    if not success:
        return success, msg
    
    delete_by_field('srs_state', 'card_id', card_id)
    delete_by_field('reviews', 'card_id', card_id)
    
    if delete('cards', card_id):
        logger.info(f"Kart silindi: {card_id}")
        return True, "Kart başarıyla silindi!"
    
    return False, "Kart silinirken bir hata oluştu."


def search_cards(query: str, deck_id: int = None) -> tuple[bool, str, list]:
    """
    Kartlarda arama yapar.
    
    Args:
        query: Arama sorgusu
        deck_id: Belirli bir deck'te arama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Bulunan kartlar)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    from deck_service import list_decks
    _, _, user_decks = list_decks()
    user_deck_ids = [d['id'] for d in user_decks]
    
    all_cards = load_json('cards')
    query_lower = query.lower()
    
    results = []
    for card in all_cards:
        if card.get('deck_id') not in user_deck_ids:
            continue
        
        if deck_id and card.get('deck_id') != deck_id:
            continue
        
        if query_lower in card.get('front', '').lower() or query_lower in card.get('back', '').lower():
            results.append(card)
    
    return True, f"{len(results)} kart bulundu.", results
>>>>>>> 49319f5dfc84fb8c02a88209b4cff51a53bda568
