"""
cli_handlers.py - CLI Akış Yöneticileri

Menü akışlarını (flow) yöneten fonksiyonlar.
main.py'nin yükünü azaltmak için ayrı modülde tutulur.
"""

from auth import register, login, logout, is_logged_in, get_current_user
from deck_service import create_deck, list_decks, update_deck, delete_deck
from card_service import create_card, list_cards, update_card, delete_card, get_card
from review_service import get_due_cards, submit_review
from report_service import print_today_summary, print_weekly_report, get_all_decks_report
from backup_service import create_backup, list_backups, export_to_csv
from utils import (
    print_header, print_success, print_error, print_warning, print_info,
    get_input, get_int_input, confirm, get_quality_description
)


def handle_login():
    """Giriş akışı."""
    print_header("🔐 Giriş Yap")
    email = get_input("E-posta: ")
    password = get_input("Parola: ")
    
    success, msg, user = login(email, password)
    if success:
        print_success(msg)
    else:
        print_error(msg)


def handle_register():
    """Kayıt akışı."""
    print_header("📝 Kayıt Ol")
    email = get_input("E-posta: ")
    password = get_input("Parola (min 6 karakter): ")
    
    success, msg, user = register(email, password)
    if success:
        print_success(msg)
        print_info("Şimdi giriş yapabilirsiniz.")
    else:
        print_error(msg)


def handle_logout():
    """Çıkış akışı."""
    success, msg = logout()
    if success:
        print_success(msg)
    else:
        print_error(msg)


def handle_list_decks():
    """Deck listeleme akışı."""
    success, msg, decks = list_decks()
    
    if not success:
        print_error(msg)
        return []
    
    print_header("📋 Deck Listesi")
    
    if not decks:
        print_info("Henüz deck oluşturulmamış.")
        return []
    
    for deck in decks:
        print(f"  [{deck['id']}] {deck['name']} - {deck.get('card_count', 0)} kart")
        if deck.get('description'):
            print(f"      📝 {deck['description']}")
    
    return decks


def handle_create_deck():
    """Deck oluşturma akışı."""
    print_header("➕ Yeni Deck Oluştur")
    name = get_input("Deck Adı: ")
    description = get_input("Açıklama (opsiyonel): ")
    
    success, msg, deck = create_deck(name, description)
    if success:
        print_success(msg)
    else:
        print_error(msg)


def handle_update_deck():
    """Deck güncelleme akışı."""
    handle_list_decks()
    print()
    
    deck_id = get_int_input("Güncellenecek Deck ID: ")
    name = get_input("Yeni Ad (boş bırakılırsa değişmez): ")
    description = get_input("Yeni Açıklama (boş bırakılırsa değişmez): ")
    
    success, msg, deck = update_deck(
        deck_id,
        name if name else None,
        description if description else None
    )
    
    if success:
        print_success(msg)
    else:
        print_error(msg)


def handle_delete_deck():
    """Deck silme akışı."""
    handle_list_decks()
    print()
    
    deck_id = get_int_input("Silinecek Deck ID: ")
    
    if confirm("Bu deck ve tüm kartları silinecek. Emin misiniz?"):
        success, msg = delete_deck(deck_id)
        if success:
            print_success(msg)
        else:
            print_error(msg)
    else:
        print_info("İptal edildi.")


def handle_list_cards(deck_id: int):
    """Kart listeleme akışı."""
    success, msg, cards = list_cards(deck_id)
    
    if not success:
        print_error(msg)
        return []
    
    print_header("📋 Kart Listesi")
    
    if not cards:
        print_info("Bu deck'te henüz kart yok.")
        return []
    
    for card in cards:
        due_info = f" (Due: {card.get('due_date', 'N/A')})" if card.get('due_date') else ""
        front_preview = card['front'][:50] + "..." if len(card['front']) > 50 else card['front']
        print(f"  [{card['id']}] {front_preview}{due_info}")
    
    return cards


def handle_create_card(deck_id: int):
    """Kart oluşturma akışı."""
    print_header("➕ Yeni Kart Ekle")
    
    while True:
        front = get_input("Ön yüz (Soru): ")
        back = get_input("Arka yüz (Cevap): ")
        
        success, msg, card = create_card(deck_id, front, back)
        if success:
            print_success(msg)
        else:
            print_error(msg)
        
        if not confirm("Başka kart eklemek ister misiniz?"):
            break


def handle_update_card(deck_id: int):
    """Kart güncelleme akışı."""
    handle_list_cards(deck_id)
    print()
    
    card_id = get_int_input("Güncellenecek Kart ID: ")
    
    success, msg, card = get_card(card_id)
    if not success:
        print_error(msg)
        return
    
    print(f"Mevcut Soru: {card['front']}")
    print(f"Mevcut Cevap: {card['back']}")
    print()
    
    front = get_input("Yeni Soru (boş bırakılırsa değişmez): ")
    back = get_input("Yeni Cevap (boş bırakılırsa değişmez): ")
    
    success, msg, updated = update_card(
        card_id,
        front if front else None,
        back if back else None
    )
    
    if success:
        print_success(msg)
    else:
        print_error(msg)


def handle_delete_card(deck_id: int):
    """Kart silme akışı."""
    handle_list_cards(deck_id)
    print()
    
    card_id = get_int_input("Silinecek Kart ID: ")
    
    if confirm("Bu kart silinecek. Emin misiniz?"):
        success, msg = delete_card(card_id)
        if success:
            print_success(msg)
        else:
            print_error(msg)
    else:
        print_info("İptal edildi.")


def handle_review_session():
    """Çalışma oturumu akışı."""
    success, msg, due_cards = get_due_cards()
    
    if not success:
        print_error(msg)
        return
    
    if not due_cards:
        print_header("🎉 Tebrikler!")
        print("Bugün çalışılacak kart kalmadı.")
        print("Yarın tekrar gel!")
        return
    
    print_header(f"📖 Bugün Çalış - {len(due_cards)} kart")
    
    for i, card in enumerate(due_cards, 1):
        print(f"\n{'='*50}")
        print(f"Kart {i}/{len(due_cards)} (Deck: {card.get('deck_name', 'Bilinmeyen')})")
        print(f"{'='*50}")
        print(f"\n📝 Soru: {card['front']}\n")
        
        input("Cevabı görmek için Enter'a basın...")
        
        print(f"\n✅ Cevap: {card['back']}\n")
        
        print("Kalite Puanı:")
        for q in range(6):
            print(f"  {q}: {get_quality_description(q)}")
        
        quality = get_int_input("Puanınız (0-5): ", 0, 5)
        
        success, msg, srs = submit_review(card['id'], quality)
        if success:
            print_success(msg)
        else:
            print_error(msg)
        
        if i < len(due_cards):
            if not confirm("Devam etmek ister misiniz?"):
                print_info("Çalışma sonlandırıldı.")
                break
    
    print_header("✨ Çalışma Tamamlandı!")
    print_today_summary()


def handle_deck_reports():
    """Deck raporları akışı."""
    success, msg, reports = get_all_decks_report()
    
    if not success:
        print_error(msg)
        return
    
    print_header("📦 Deck Raporları")
    
    if not reports:
        print_info("Henüz deck oluşturulmamış.")
        return
    
    for report in reports:
        print(f"\n📦 {report['deck_name']}")
        print(f"   Toplam Kart: {report['total_cards']}")
        print(f"   Bugün Due: {report['due_today']}")
        print(f"   Ortalama EF: {report['average_ef']}")
        
        mastery = report['mastery_distribution']
        total = report['total_cards']
        if total > 0:
            print(f"   Öğrenme: {mastery['learning']} | İnceleme: {mastery['reviewing']} | Ustalaşmış: {mastery['mastered']}")


def handle_backup():
    """Yedekleme akışı."""
    print_header("💾 Yedekleme")
    
    if confirm("Tüm veriler yedeklensin mi?"):
        success, msg = create_backup()
        if success:
            print_success(msg)
        else:
            print_error(msg)


def handle_list_backups():
    """Yedek listeleme akışı."""
    success, msg, backups = list_backups()
    
    print_header("📁 Yedekler")
    
    if not backups:
        print_info(msg)
        return
    
    for backup in backups:
        print(f"  [{backup['name']}] {backup['size_mb']} MB")


def handle_export_csv():
    """CSV dışa aktarma akışı."""
    print_header("📄 CSV Dışa Aktar")
    
    if confirm("Kartlar CSV olarak dışa aktarılsın mı?"):
        success, msg = export_to_csv()
        if success:
            print_success(msg)
        else:
            print_error(msg)


def handle_import_csv():
    """CSV içe aktarma akışı."""
    from backup_service import import_from_csv
    
    print_header("📥 CSV İçe Aktar")
    print("CSV formatı: front,back (soru,cevap)")
    print()
    
    decks = handle_list_decks()
    if not decks:
        return
    
    print()
    deck_id = get_int_input("Kartların ekleneceği Deck ID: ")
    
    selected = next((d for d in decks if d['id'] == deck_id), None)
    if not selected:
        print_error("Geçersiz Deck ID.")
        return
    
    file_path = get_input("CSV dosya yolu: ")
    
    if confirm(f"'{selected['name']}' deck'ine kartlar eklensin mi?"):
        success, msg, count = import_from_csv(file_path, deck_id)
        if success:
            print_success(msg)
        else:
            print_error(msg)


def handle_search_cards():
    """Kart arama akışı."""
    from card_service import search_cards
    
    print_header("🔍 Kart Ara")
    
    query = get_input("Aranacak kelime: ")
    
    if not query.strip():
        print_warning("Arama terimi boş olamaz.")
        return
    
    print("\nTüm deck'lerde aramak için 0 girin.")
    decks = handle_list_decks()
    print()
    
    deck_filter = get_int_input("Deck ID (0 = hepsi): ", 0)
    deck_id = deck_filter if deck_filter > 0 else None
    
    success, msg, results = search_cards(query, deck_id)
    
    if not success:
        print_error(msg)
        return
    
    print_header(f"🔍 Arama Sonuçları: '{query}'")
    
    if not results:
        print_info("Sonuç bulunamadı.")
        return
    
    print(f"{len(results)} kart bulundu:\n")
    
    for card in results:
        print(f"  [{card['id']}] Deck: {card.get('deck_id', '?')}")
        print(f"      Soru: {card['front'][:60]}...")
        print(f"      Cevap: {card['back'][:60]}...")
        print()


def handle_filter_due_by_deck():
    """Deck'e göre due kartları filtrele."""
    from review_service import get_due_cards
    
    print_header("📋 Deck'e Göre Due Kartlar")
    
    decks = handle_list_decks()
    if not decks:
        return
    
    print()
    deck_id = get_int_input("Deck ID: ")
    
    success, msg, due_cards = get_due_cards(deck_id)
    
    if not success:
        print_error(msg)
        return
    
    if not due_cards:
        print_info("Bu deck'te bugün due kart yok.")
        return
    
    print(f"\n{len(due_cards)} kart due:\n")
    for card in due_cards:
        print(f"  [{card['id']}] {card['front'][:50]}...")

