<<<<<<< HEAD
"""
deck_service.py - Deste Yönetimi Modülü

Deck (deste) CRUD işlemlerini yönetir.
Her deck bir kullanıcıya aittir ve kartları içerir.
"""

import logging
from storage import (
    load_json, save_json, find_by_id, find_all_by_field,
    insert, update, delete, delete_by_field
)
from auth import get_current_user_id, is_logged_in

logger = logging.getLogger(__name__)


def create_deck(name: str, description: str = "") -> tuple[bool, str, dict | None]:
    """
    Yeni deck oluşturur.
    
    Args:
        name: Deck adı
        description: Açıklama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    if not name or not name.strip():
        return False, "Deck adı boş olamaz.", None
    
    user_decks = find_all_by_field('decks', 'user_id', user_id)
    for deck in user_decks:
        if deck['name'].lower() == name.strip().lower():
            return False, "Bu isimde bir deck zaten mevcut.", None
    
    deck = {
        'user_id': user_id,
        'name': name.strip(),
        'description': description.strip() if description else ""
    }
    
    saved_deck = insert('decks', deck)
    logger.info(f"Deck oluşturuldu: {name} (ID: {saved_deck['id']}, User: {user_id})")
    
    return True, f"Deck '{name}' başarıyla oluşturuldu!", saved_deck


def list_decks() -> tuple[bool, str, list]:
    """
    Kullanıcının tüm decklerini listeler.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck listesi)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    decks = find_all_by_field('decks', 'user_id', user_id)
    
    cards = load_json('cards')
    for deck in decks:
        deck_cards = [c for c in cards if c.get('deck_id') == deck['id']]
        deck['card_count'] = len(deck_cards)
    
    return True, f"{len(decks)} deck bulundu.", decks


def get_deck(deck_id: int) -> tuple[bool, str, dict | None]:
    """
    ID'ye göre deck getirir.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    deck = find_by_id('decks', deck_id)
    
    if not deck:
        return False, "Deck bulunamadı.", None
    
    if deck.get('user_id') != user_id:
        logger.warning(f"Yetkisiz deck erişimi: User {user_id} -> Deck {deck_id}")
        return False, "Bu deck'e erişim izniniz yok.", None
    
    return True, "Deck bulundu.", deck


def update_deck(deck_id: int, name: str = None, description: str = None) -> tuple[bool, str, dict | None]:
    """
    Deck bilgilerini günceller.
    
    Args:
        deck_id: Deck ID
        name: Yeni ad (opsiyonel)
        description: Yeni açıklama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel deck verisi veya None)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg, None
    
    updates = {}
    
    if name is not None:
        if not name.strip():
            return False, "Deck adı boş olamaz.", None
        updates['name'] = name.strip()
    
    if description is not None:
        updates['description'] = description.strip()
    
    if not updates:
        return False, "Güncellenecek bir alan belirtilmedi.", None
    
    updated_deck = update('decks', deck_id, updates)
    
    if updated_deck:
        logger.info(f"Deck güncellendi: {deck_id}")
        return True, "Deck başarıyla güncellendi!", updated_deck
    
    return False, "Deck güncellenirken bir hata oluştu.", None


def delete_deck(deck_id: int) -> tuple[bool, str]:
    """
    Deck'i ve bağlı tüm kartları siler (cascade).
    
    Args:
        deck_id: Silinecek deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg
    
    deck_name = deck['name']
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    card_ids = [c['id'] for c in cards]
    
    for card_id in card_ids:
        delete_by_field('srs_state', 'card_id', card_id)
        delete_by_field('reviews', 'card_id', card_id)
    
    deleted_cards = delete_by_field('cards', 'deck_id', deck_id)
    
    if delete('decks', deck_id):
        logger.info(f"Deck silindi (cascade): {deck_name} (ID: {deck_id}, Kartlar: {deleted_cards})")
        return True, f"Deck '{deck_name}' ve {deleted_cards} kart silindi."
    
    return False, "Deck silinirken bir hata oluştu."


def get_deck_stats(deck_id: int) -> tuple[bool, str, dict | None]:
    """
    Deck istatistiklerini döndürür.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, İstatistikler veya None)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg, None
    
    from utils import get_today_str
    
    user_id = get_current_user_id()
    today = get_today_str()
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    card_ids = [c['id'] for c in cards]
    
    srs_states = load_json('srs_state')
    deck_srs = [s for s in srs_states if s.get('card_id') in card_ids and s.get('user_id') == user_id]
    
    due_count = sum(1 for s in deck_srs if s.get('due_date', '') <= today)
    
    ef_values = [s.get('ef', 2.5) for s in deck_srs]
    avg_ef = sum(ef_values) / len(ef_values) if ef_values else 2.5
    
    stats = {
        'deck_id': deck_id,
        'deck_name': deck['name'],
        'total_cards': len(cards),
        'due_cards': due_count,
        'average_ef': round(avg_ef, 2)
    }
    
    return True, "İstatistikler hesaplandı.", stats
=======
"""
deck_service.py - Deste Yönetimi Modülü

Deck (deste) CRUD işlemlerini yönetir.
Her deck bir kullanıcıya aittir ve kartları içerir.
"""

import logging
from storage import (
    load_json, save_json, find_by_id, find_all_by_field,
    insert, update, delete, delete_by_field
)
from auth import get_current_user_id, is_logged_in

logger = logging.getLogger(__name__)


def create_deck(name: str, description: str = "") -> tuple[bool, str, dict | None]:
    """
    Yeni deck oluşturur.
    
    Args:
        name: Deck adı
        description: Açıklama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    if not name or not name.strip():
        return False, "Deck adı boş olamaz.", None
    
    user_decks = find_all_by_field('decks', 'user_id', user_id)
    for deck in user_decks:
        if deck['name'].lower() == name.strip().lower():
            return False, "Bu isimde bir deck zaten mevcut.", None
    
    deck = {
        'user_id': user_id,
        'name': name.strip(),
        'description': description.strip() if description else ""
    }
    
    saved_deck = insert('decks', deck)
    logger.info(f"Deck oluşturuldu: {name} (ID: {saved_deck['id']}, User: {user_id})")
    
    return True, f"Deck '{name}' başarıyla oluşturuldu!", saved_deck


def list_decks() -> tuple[bool, str, list]:
    """
    Kullanıcının tüm decklerini listeler.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck listesi)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", []
    
    decks = find_all_by_field('decks', 'user_id', user_id)
    
    cards = load_json('cards')
    for deck in decks:
        deck_cards = [c for c in cards if c.get('deck_id') == deck['id']]
        deck['card_count'] = len(deck_cards)
    
    return True, f"{len(decks)} deck bulundu.", decks


def get_deck(deck_id: int) -> tuple[bool, str, dict | None]:
    """
    ID'ye göre deck getirir.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Deck verisi veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    deck = find_by_id('decks', deck_id)
    
    if not deck:
        return False, "Deck bulunamadı.", None
    
    if deck.get('user_id') != user_id:
        logger.warning(f"Yetkisiz deck erişimi: User {user_id} -> Deck {deck_id}")
        return False, "Bu deck'e erişim izniniz yok.", None
    
    return True, "Deck bulundu.", deck


def update_deck(deck_id: int, name: str = None, description: str = None) -> tuple[bool, str, dict | None]:
    """
    Deck bilgilerini günceller.
    
    Args:
        deck_id: Deck ID
        name: Yeni ad (opsiyonel)
        description: Yeni açıklama (opsiyonel)
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Güncel deck verisi veya None)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg, None
    
    updates = {}
    
    if name is not None:
        if not name.strip():
            return False, "Deck adı boş olamaz.", None
        updates['name'] = name.strip()
    
    if description is not None:
        updates['description'] = description.strip()
    
    if not updates:
        return False, "Güncellenecek bir alan belirtilmedi.", None
    
    updated_deck = update('decks', deck_id, updates)
    
    if updated_deck:
        logger.info(f"Deck güncellendi: {deck_id}")
        return True, "Deck başarıyla güncellendi!", updated_deck
    
    return False, "Deck güncellenirken bir hata oluştu.", None


def delete_deck(deck_id: int) -> tuple[bool, str]:
    """
    Deck'i ve bağlı tüm kartları siler (cascade).
    
    Args:
        deck_id: Silinecek deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg
    
    deck_name = deck['name']
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    card_ids = [c['id'] for c in cards]
    
    for card_id in card_ids:
        delete_by_field('srs_state', 'card_id', card_id)
        delete_by_field('reviews', 'card_id', card_id)
    
    deleted_cards = delete_by_field('cards', 'deck_id', deck_id)
    
    if delete('decks', deck_id):
        logger.info(f"Deck silindi (cascade): {deck_name} (ID: {deck_id}, Kartlar: {deleted_cards})")
        return True, f"Deck '{deck_name}' ve {deleted_cards} kart silindi."
    
    return False, "Deck silinirken bir hata oluştu."


def get_deck_stats(deck_id: int) -> tuple[bool, str, dict | None]:
    """
    Deck istatistiklerini döndürür.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, İstatistikler veya None)
    """
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg, None
    
    from utils import get_today_str
    
    user_id = get_current_user_id()
    today = get_today_str()
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    card_ids = [c['id'] for c in cards]
    
    srs_states = load_json('srs_state')
    deck_srs = [s for s in srs_states if s.get('card_id') in card_ids and s.get('user_id') == user_id]
    
    due_count = sum(1 for s in deck_srs if s.get('due_date', '') <= today)
    
    ef_values = [s.get('ef', 2.5) for s in deck_srs]
    avg_ef = sum(ef_values) / len(ef_values) if ef_values else 2.5
    
    stats = {
        'deck_id': deck_id,
        'deck_name': deck['name'],
        'total_cards': len(cards),
        'due_cards': due_count,
        'average_ef': round(avg_ef, 2)
    }
    
    return True, "İstatistikler hesaplandı.", stats
>>>>>>> 49319f5dfc84fb8c02a88209b4cff51a53bda568
