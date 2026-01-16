"""
report_service.py - Raporlama Modülü

İstatistikler ve raporlar oluşturur.
Due kartları, haftalık performans ve deck bazlı analizler sunar.
"""

import logging
from datetime import datetime, timedelta
from storage import load_json, find_all_by_field
from auth import get_current_user_id
from utils import get_today_str, parse_date

logger = logging.getLogger(__name__)


def get_today_summary() -> tuple[bool, str, dict | None]:
    """
    Bugünün özetini döndürür.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Özet veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    today = get_today_str()
    
    srs_states = find_all_by_field('srs_state', 'user_id', user_id)
    due_count = sum(1 for s in srs_states if s.get('due_date', '') <= today)
    
    reviews = find_all_by_field('reviews', 'user_id', user_id)
    today_reviews = [r for r in reviews if r.get('reviewed_at', '').startswith(today)]
    
    if today_reviews:
        avg_quality = sum(r.get('quality', 0) for r in today_reviews) / len(today_reviews)
    else:
        avg_quality = 0
    
    summary = {
        'date': today,
        'due_cards': due_count,
        'reviewed_today': len(today_reviews),
        'average_quality': round(avg_quality, 2)
    }
    
    return True, "Bugünün özeti hazırlandı.", summary


def get_weekly_stats() -> tuple[bool, str, dict | None]:
    """
    Son 7 günün istatistiklerini döndürür.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, İstatistikler veya None)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "Bu işlem için giriş yapmalısınız.", None
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    reviews = find_all_by_field('reviews', 'user_id', user_id)
    
    weekly_reviews = []
    for r in reviews:
        reviewed_at = r.get('reviewed_at', '')
        try:
            review_date = datetime.fromisoformat(reviewed_at)
            if review_date >= week_ago:
                weekly_reviews.append(r)
        except:
            continue
    
    daily_counts = {}
    daily_qualities = {}
    
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_counts[date] = 0
        daily_qualities[date] = []
    
    for r in weekly_reviews:
        date = r.get('reviewed_at', '')[:10]
        if date in daily_counts:
            daily_counts[date] += 1
            daily_qualities[date].append(r.get('quality', 0))
    
    total_reviews = len(weekly_reviews)
    total_quality = sum(r.get('quality', 0) for r in weekly_reviews)
    avg_quality = total_quality / total_reviews if total_reviews > 0 else 0
    
    stats = {
        'period': 'Son 7 gün',
        'total_reviews': total_reviews,
        'average_quality': round(avg_quality, 2),
        'daily_breakdown': [
            {
                'date': date,
                'count': daily_counts[date],
                'avg_quality': round(sum(daily_qualities[date]) / len(daily_qualities[date]), 2) if daily_qualities[date] else 0
            }
            for date in sorted(daily_counts.keys(), reverse=True)
        ]
    }
    
    return True, "Haftalık istatistikler hazırlandı.", stats


def get_deck_report(deck_id: int) -> tuple[bool, str, dict | None]:
    """
    Deck bazlı rapor döndürür.
    
    Args:
        deck_id: Deck ID
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Rapor veya None)
    """
    from deck_service import get_deck
    
    success, msg, deck = get_deck(deck_id)
    if not success:
        return success, msg, None
    
    user_id = get_current_user_id()
    today = get_today_str()
    
    cards = find_all_by_field('cards', 'deck_id', deck_id)
    card_ids = [c['id'] for c in cards]
    
    srs_states = load_json('srs_state')
    deck_srs = [s for s in srs_states if s.get('card_id') in card_ids and s.get('user_id') == user_id]
    
    due_count = sum(1 for s in deck_srs if s.get('due_date', '') <= today)
    ef_values = [s.get('ef', 2.5) for s in deck_srs]
    avg_ef = sum(ef_values) / len(ef_values) if ef_values else 2.5
    
    mastery = {
        'learning': sum(1 for ef in ef_values if ef < 2.0),
        'reviewing': sum(1 for ef in ef_values if 2.0 <= ef < 2.5),
        'mastered': sum(1 for ef in ef_values if ef >= 2.5)
    }
    
    report = {
        'deck_id': deck_id,
        'deck_name': deck['name'],
        'total_cards': len(cards),
        'due_today': due_count,
        'average_ef': round(avg_ef, 2),
        'mastery_distribution': mastery
    }
    
    return True, "Deck raporu hazırlandı.", report


def get_all_decks_report() -> tuple[bool, str, list]:
    """
    Tüm decks için özet rapor döndürür.
    
    Returns:
        tuple: (Başarılı mı, Mesaj, Raporlar listesi)
    """
    from deck_service import list_decks
    
    success, msg, decks = list_decks()
    if not success:
        return success, msg, []
    
    reports = []
    for deck in decks:
        _, _, report = get_deck_report(deck['id'])
        if report:
            reports.append(report)
    
    return True, f"{len(reports)} deck raporu hazırlandı.", reports


def print_weekly_report():
    """
    Haftalık raporu formatlı yazdırır.
    """
    from utils import print_header
    
    success, _, stats = get_weekly_stats()
    if not success:
        print("❌ Rapor oluşturulamadı.")
        return
    
    print_header("📊 Haftalık Rapor")
    print(f"Toplam Review: {stats['total_reviews']}")
    print(f"Ortalama Kalite: {stats['average_quality']}/5")
    print()
    print("Günlük Dağılım:")
    print("-" * 40)
    
    for day in stats['daily_breakdown']:
        bar = "█" * day['count'] if day['count'] <= 20 else "█" * 20 + f"... ({day['count']})"
        print(f"{day['date']}: {bar} ({day['count']} review, avg: {day['avg_quality']})")


def print_today_summary():
    """
    Bugünün özetini formatlı yazdırır.
    """
    from utils import print_header
    
    success, _, summary = get_today_summary()
    if not success:
        print("❌ Özet oluşturulamadı.")
        return
    
    print_header(f"📅 Bugün: {summary['date']}")
    print(f"Due Kartlar: {summary['due_cards']}")
    print(f"Bugün Yapılan Review: {summary['reviewed_today']}")
    print(f"Bugünkü Ortalama Kalite: {summary['average_quality']}/5")
