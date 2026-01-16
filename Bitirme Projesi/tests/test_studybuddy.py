"""
test_studybuddy.py - StudyBuddy Birim Testleri

Minimum 10 test içerir.
Çalıştırma: python -m unittest tests.test_studybuddy
"""

import unittest
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def setup_test_environment():
    """Test ortamını hazırlar."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    import storage
    storage.DATA_DIR = TEST_DATA_DIR
    storage.ensure_data_dir()


def cleanup_test_environment():
    """Test ortamını temizler."""
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


class TestAuth(unittest.TestCase):
    """Kimlik doğrulama testleri."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def setUp(self):
        """Her test öncesi oturumu temizle."""
        from auth import logout, _current_session
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        
        import storage
        storage.save_json('users', [])
    
    def test_register_success(self):
        """Başarılı kayıt testi."""
        from auth import register
        
        success, msg, user = register("test@example.com", "password123")
        
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], "test@example.com")
    
    def test_register_duplicate_email(self):
        """Aynı email ile ikinci kayıt engellenir."""
        from auth import register
        
        register("duplicate@example.com", "password123")
        
        success, msg, user = register("duplicate@example.com", "password456")
        
        self.assertFalse(success)
        self.assertIn("zaten kayıtlı", msg.lower())
    
    def test_login_wrong_password(self):
        """Yanlış parola reddedilir."""
        from auth import register, login
        
        register("wrongpass@example.com", "correctpassword")
        
        success, msg, user = login("wrongpass@example.com", "wrongpassword")
        
        self.assertFalse(success)
        self.assertIn("hatalı", msg.lower())
    
    def test_login_success(self):
        """Başarılı giriş testi."""
        from auth import register, login
        
        register("login@example.com", "mypassword")
        
        success, msg, user = login("login@example.com", "mypassword")
        
        self.assertTrue(success)
        self.assertIsNotNone(user)


class TestDeck(unittest.TestCase):
    """Deck CRUD testleri."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def setUp(self):
        """Her test öncesi kullanıcı oluştur ve giriş yap."""
        from auth import register, login, logout, _current_session
        import storage
                
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        
        storage.save_json('users', [])
        storage.save_json('decks', [])
        storage.save_json('cards', [])
        storage.save_json('srs_state', [])
        
        register("decktest@example.com", "password123")
        login("decktest@example.com", "password123")
    
    def test_deck_crud(self):
        """Deck oluştur-listele-güncelle-sil akışı."""
        from deck_service import create_deck, list_decks, update_deck, delete_deck
        
        success, msg, deck = create_deck("Python Basics", "Temel Python")
        self.assertTrue(success)
        self.assertIsNotNone(deck)
        deck_id = deck['id']
        
        success, msg, decks = list_decks()
        self.assertTrue(success)
        self.assertEqual(len(decks), 1)
        
        success, msg, updated = update_deck(deck_id, name="Advanced Python")
        self.assertTrue(success)
        self.assertEqual(updated['name'], "Advanced Python")
        
        success, msg = delete_deck(deck_id)
        self.assertTrue(success)
        
        success, msg, decks = list_decks()
        self.assertEqual(len(decks), 0)


class TestCard(unittest.TestCase):
    """Card CRUD testleri."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def setUp(self):
        """Her test öncesi kullanıcı ve deck oluştur."""
        from auth import register, login, _current_session
        from deck_service import create_deck
        import storage
        
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        
        storage.save_json('users', [])
        storage.save_json('decks', [])
        storage.save_json('cards', [])
        storage.save_json('srs_state', [])
        storage.save_json('reviews', [])
        
        register("cardtest@example.com", "password123")
        login("cardtest@example.com", "password123")
        
        success, msg, deck = create_deck("Test Deck", "Test")
        self.deck_id = deck['id']
    
    def test_card_crud(self):
        """Kart oluştur-listele-güncelle-sil akışı."""
        from card_service import create_card, list_cards, update_card, delete_card
        
        success, msg, card = create_card(self.deck_id, "What is Python?", "A programming language")
        self.assertTrue(success)
        self.assertIsNotNone(card)
        card_id = card['id']
        
        success, msg, cards = list_cards(self.deck_id)
        self.assertTrue(success)
        self.assertEqual(len(cards), 1)
        
        success, msg, updated = update_card(card_id, front="What is Python 3?")
        self.assertTrue(success)
        self.assertIn("Python 3", updated['front'])
        
        success, msg = delete_card(card_id)
        self.assertTrue(success)
        
        success, msg, cards = list_cards(self.deck_id)
        self.assertEqual(len(cards), 0)


class TestReview(unittest.TestCase):
    """Review ve SM-2 testleri."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def setUp(self):
        """Her test öncesi kullanıcı, deck ve kart oluştur."""
        from auth import register, login, _current_session
        from deck_service import create_deck
        from card_service import create_card
        import storage
        
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        
        storage.save_json('users', [])
        storage.save_json('decks', [])
        storage.save_json('cards', [])
        storage.save_json('srs_state', [])
        storage.save_json('reviews', [])
        
        register("reviewtest@example.com", "password123")
        login("reviewtest@example.com", "password123")
        
        success, msg, deck = create_deck("Review Test", "Test")
        self.deck_id = deck['id']
        
        success, msg, card = create_card(self.deck_id, "Test Question", "Test Answer")
        self.card_id = card['id']
    
    def test_review_quality_low(self):
        """quality<3 durumunda repetition resetlenir ve due_date = today+1 olur."""
        from review_service import submit_review, get_srs_state
        from utils import get_today_str, add_days
        
        success, msg, srs = submit_review(self.card_id, 2)
        
        self.assertTrue(success)
        
        success, msg, state = get_srs_state(self.card_id)
        
        self.assertEqual(state['repetition'], 0)
        self.assertEqual(state['interval_days'], 1)
        
        expected_due = add_days(get_today_str(), 1)
        self.assertEqual(state['due_date'], expected_due)
    
    def test_review_quality_high(self):
        """quality>=3 durumunda interval büyür."""
        from review_service import submit_review, get_srs_state
        
        success, msg, srs = submit_review(self.card_id, 4)
        
        self.assertTrue(success)
        
        success, msg, state = get_srs_state(self.card_id)
        
        self.assertEqual(state['repetition'], 1)
        self.assertEqual(state['interval_days'], 1)     
    
    def test_due_list(self):
        """due_date <= today olan kartlar listelenir."""
        from review_service import get_due_cards
        
        success, msg, due_cards = get_due_cards()
        
        self.assertTrue(success)
        self.assertEqual(len(due_cards), 1)


class TestCascadeDelete(unittest.TestCase):
    """Cascade silme testi."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def test_cascade_delete(self):
        """Deck silinince bağlı card ve srs_state kayıtları da silinir."""
        from auth import register, login, _current_session
        from deck_service import create_deck, delete_deck
        from card_service import create_card
        import storage
        
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        
        storage.save_json('users', [])
        storage.save_json('decks', [])
        storage.save_json('cards', [])
        storage.save_json('srs_state', [])
        
        register("cascade@example.com", "password123")
        login("cascade@example.com", "password123")
        
        success, msg, deck = create_deck("Cascade Test", "")
        deck_id = deck['id']
        
        create_card(deck_id, "Q1", "A1")
        create_card(deck_id, "Q2", "A2")
        
        cards_before = storage.load_json('cards')
        srs_before = storage.load_json('srs_state')
        self.assertEqual(len([c for c in cards_before if c['deck_id'] == deck_id]), 2)
        
        delete_deck(deck_id)
        
        cards_after = storage.load_json('cards')
        srs_after = storage.load_json('srs_state')
        
        self.assertEqual(len([c for c in cards_after if c.get('deck_id') == deck_id]), 0)


class TestUserIsolation(unittest.TestCase):
    """Kullanıcı izolasyonu testi."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def test_user_isolation(self):
        """Farklı kullanıcı deck/kart verilerini göremez."""
        from auth import register, login, logout, _current_session
        from deck_service import create_deck, list_decks
        import storage
        
        _current_session['user_id'] = None
        _current_session['email'] = None
        _current_session['logged_in'] = False
        storage.save_json('users', [])
        storage.save_json('decks', [])
        
        register("user1@example.com", "password123")
        login("user1@example.com", "password123")
        create_deck("User1 Deck", "")
        logout()
        
        register("user2@example.com", "password123")
        login("user2@example.com", "password123")
        
        success, msg, user2_decks = list_decks()
        
        self.assertEqual(len(user2_decks), 0)


class TestAtomicWrite(unittest.TestCase):
    """Atomic write testi."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
    
    def test_atomic_write(self):
        """Atomic write ile kaydedilen JSON bozulmaz."""
        import storage
        
        test_data = [
            {"id": 1, "name": "Test 1"},
            {"id": 2, "name": "Test 2"},
            {"id": 3, "name": "Türkçe karakterler: ğüşıöç"}
        ]
        
        result = storage.save_json('decks', test_data)
        self.assertTrue(result)
        
        loaded_data = storage.load_json('decks')
        
        self.assertEqual(len(loaded_data), 3)
        self.assertEqual(loaded_data[2]['name'], "Türkçe karakterler: ğüşıöç")


class TestSM2Algorithm(unittest.TestCase):
    """SM-2 algoritması testi."""
    
    def test_sm2_quality_zero(self):
        """Kalite 0 ise repetition sıfırlanır."""
        from review_service import calculate_sm2
        
        rep, ef, interval = calculate_sm2(0, 3, 2.5, 10)
        
        self.assertEqual(rep, 0)
        self.assertEqual(interval, 1)
    
    def test_sm2_quality_five(self):
        """Kalite 5 ise interval artar."""
        from review_service import calculate_sm2
        
        rep, ef, interval = calculate_sm2(5, 0, 2.5, 1)
        self.assertEqual(rep, 1)
        self.assertEqual(interval, 1)
        
        rep, ef, interval = calculate_sm2(5, 1, ef, 1)
        self.assertEqual(rep, 2)
        self.assertEqual(interval, 6)
        
        rep, ef, interval = calculate_sm2(5, 2, ef, 6)
        self.assertEqual(rep, 3)
        self.assertGreater(interval, 6)
    
    def test_sm2_ef_minimum(self):
        """EF minimum 1.3 olmalı."""
        from review_service import calculate_sm2
        
        rep, ef, interval = calculate_sm2(0, 3, 1.5, 10)
        
        self.assertGreaterEqual(ef, 1.3)


class TestBackupService(unittest.TestCase):
    """Yedekleme servisi testleri."""
    
    @classmethod
    def setUpClass(cls):
        setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        cleanup_test_environment()
        backup_dir = Path(__file__).parent / "test_backups"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
    
    def setUp(self):
        """Test ortamını hazırla."""
        import storage
        import backup_service
        
        backup_service.DATA_DIR = TEST_DATA_DIR
        backup_service.BACKUP_DIR = Path(__file__).parent / "test_backups"
        
        storage.save_json('cards', [
            {"id": 1, "front": "Test", "back": "Answer"}
        ])
    
    def test_create_backup(self):
        """Yedek oluşturma testi."""
        from backup_service import create_backup, BACKUP_DIR
        
        success, msg = create_backup()
        
        self.assertTrue(success)
        self.assertIn("Yedek oluşturuldu", msg)
        
        self.assertTrue(BACKUP_DIR.exists())
    
    def test_list_backups(self):
        """Yedek listeleme testi."""
        from backup_service import create_backup, list_backups
        
        create_backup()
        
        success, msg, backups = list_backups()
        
        self.assertTrue(success)
        self.assertGreater(len(backups), 0)
    
    def test_export_csv(self):
        """CSV dışa aktarma testi."""
        from backup_service import export_to_csv, BACKUP_DIR
        
        success, msg = export_to_csv()
        
        self.assertTrue(success)
        self.assertIn("CSV", msg)


if __name__ == '__main__':
    unittest.main()
