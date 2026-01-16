"""
main.py - StudyBuddy Ana Giriş Noktası

CLI menü sistemi ile uygulamayı başlatır.
python main.py ile çalıştırılır.

Not: İş mantığı cli_handlers.py ve servis modüllerinde,
     bu dosya sadece menü yapısını yönetir.
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('studybuddy.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

from auth import is_logged_in, get_current_user, logout
from deck_service import list_decks
from report_service import print_today_summary, print_weekly_report
from utils import print_header, print_warning, get_int_input

from cli_handlers import (
    handle_login, handle_register, handle_logout,
    handle_list_decks, handle_create_deck, handle_update_deck, handle_delete_deck,
    handle_list_cards, handle_create_card, handle_update_card, handle_delete_card,
    handle_review_session, handle_deck_reports,
    handle_backup, handle_list_backups, handle_export_csv, handle_import_csv,
    handle_search_cards, handle_filter_due_by_deck
)


def show_main_menu() -> int:
    """Ana menüyü gösterir ve seçimi döner."""
    print_header("📚 StudyBuddy - Ana Menü")
    
    user = get_current_user()
    if user:
        print(f"👤 Giriş yapan: {user['email']}")
        print()
    
    print("1) Kayıt / Giriş")
    print("2) Deck İşlemleri")
    print("3) Kart İşlemleri")
    print("4) Bugün Çalış")
    print("5) Raporlar")
    print("6) Arama")
    print("7) Yedekleme & Import")
    print("8) Çıkış")
    print()
    return get_int_input("Seçiminiz: ", 1, 8)


def auth_menu():
    """Kimlik doğrulama menüsü."""
    while True:
        print_header("👤 Kullanıcı İşlemleri")
        
        if is_logged_in():
            user = get_current_user()
            print(f"Giriş yapan: {user['email']}\n")
            print("1) Çıkış Yap")
            print("2) Ana Menüye Dön")
            
            choice = get_int_input("Seçiminiz: ", 1, 2)
            if choice == 1:
                handle_logout()
            else:
                return
        else:
            print("1) Giriş Yap")
            print("2) Kayıt Ol")
            print("3) Ana Menüye Dön")
            
            choice = get_int_input("Seçiminiz: ", 1, 3)
            if choice == 1:
                handle_login()
            elif choice == 2:
                handle_register()
            else:
                return


def deck_menu():
    """Deck menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    
    while True:
        print_header("📦 Deck İşlemleri")
        print("1) Deck Listele")
        print("2) Deck Oluştur")
        print("3) Deck Güncelle")
        print("4) Deck Sil")
        print("5) Ana Menüye Dön")
        
        choice = get_int_input("Seçiminiz: ", 1, 5)
        
        actions = {
            1: handle_list_decks,
            2: handle_create_deck,
            3: handle_update_deck,
            4: handle_delete_deck,
            5: lambda: None
        }
        
        if choice == 5:
            return
        actions[choice]()


def card_menu():
    """Kart menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    
    success, msg, decks = list_decks()
    if not success or not decks:
        print_warning("Önce bir deck oluşturmalısınız.")
        return
    
    print_header("📦 Deck Seçin")
    for deck in decks:
        print(f"  [{deck['id']}] {deck['name']}")
    
    deck_id = get_int_input("Deck ID: ")
    selected = next((d for d in decks if d['id'] == deck_id), None)
    
    if not selected:
        print_warning("Geçersiz Deck ID.")
        return
    
    while True:
        print_header(f"🃏 Kart İşlemleri - {selected['name']}")
        print("1) Kart Listele")
        print("2) Kart Ekle")
        print("3) Kart Güncelle")
        print("4) Kart Sil")
        print("5) Geri Dön")
        
        choice = get_int_input("Seçiminiz: ", 1, 5)
        
        if choice == 5:
            return
        elif choice == 1:
            handle_list_cards(deck_id)
        elif choice == 2:
            handle_create_card(deck_id)
        elif choice == 3:
            handle_update_card(deck_id)
        elif choice == 4:
            handle_delete_card(deck_id)


def review_menu():
    """Çalışma menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    handle_review_session()


def report_menu():
    """Rapor menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    
    while True:
        print_header("📊 Raporlar")
        print("1) Bugünün Özeti")
        print("2) Haftalık Rapor")
        print("3) Deck Raporları")
        print("4) Geri Dön")
        
        choice = get_int_input("Seçiminiz: ", 1, 4)
        
        if choice == 4:
            return
        elif choice == 1:
            print_today_summary()
        elif choice == 2:
            print_weekly_report()
        elif choice == 3:
            handle_deck_reports()
        
        input("\nDevam etmek için Enter'a basın...")


def search_menu():
    """Arama menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    
    while True:
        print_header("🔍 Arama & Filtreleme")
        print("1) Kart Ara")
        print("2) Deck'e Göre Due Kartlar")
        print("3) Geri Dön")
        
        choice = get_int_input("Seçiminiz: ", 1, 3)
        
        if choice == 3:
            return
        elif choice == 1:
            handle_search_cards()
        elif choice == 2:
            handle_filter_due_by_deck()
        
        input("\nDevam etmek için Enter'a basın...")


def backup_menu():
    """Yedekleme ve import menüsü."""
    if not is_logged_in():
        print_warning("Bu işlem için giriş yapmalısınız.")
        return
    
    while True:
        print_header("💾 Yedekleme & Import")
        print("1) Yedek Oluştur")
        print("2) Yedekleri Listele")
        print("3) CSV Dışa Aktar")
        print("4) CSV İçe Aktar")
        print("5) Geri Dön")
        
        choice = get_int_input("Seçiminiz: ", 1, 5)
        
        if choice == 5:
            return
        elif choice == 1:
            handle_backup()
        elif choice == 2:
            handle_list_backups()
        elif choice == 3:
            handle_export_csv()
        elif choice == 4:
            handle_import_csv()


def main():
    """Ana fonksiyon."""
    print("\n" + "=" * 50)
    print("    📚 StudyBuddy'ye Hoş Geldiniz!")
    print("    Aralıklı Tekrar Sistemi")
    print("=" * 50)
    
    logger.info("Uygulama başlatıldı")
    
    menus = {
        1: auth_menu,
        2: deck_menu,
        3: card_menu,
        4: review_menu,
        5: report_menu,
        6: search_menu,
        7: backup_menu
    }
    
    while True:
        try:
            choice = show_main_menu()
            
            if choice == 8:
                if is_logged_in():
                    logout()
                print("\n👋 Görüşmek üzere! İyi çalışmalar!")
                logger.info("Uygulama kapatıldı")
                break
            
            menus[choice]()
            
        except KeyboardInterrupt:
            print("\n\n👋 Uygulama kapatılıyor...")
            if is_logged_in():
                logout()
            logger.info("Uygulama kullanıcı tarafından kapatıldı")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            logger.error(f"Beklenmeyen hata: {e}", exc_info=True)


if __name__ == "__main__":
    main()
