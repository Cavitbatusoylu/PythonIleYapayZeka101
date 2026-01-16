# StudyBuddy - Bitirme Projesi Uygulama Planı

**Proje:** Techcareer.net Python ile Yapay Zeka Eğitimi Bitirme Projesi  
**Amaç:** Aralıklı tekrar (spaced repetition) sistemi ile CLI tabanlı flashcard uygulaması

---

## 📋 Proje Özeti

StudyBuddy, öğrencinin kendi çalışma materyalini (flashcard) oluşturduğu, kartları çalıştıkça 0-5 arası puanladığı ve SM-2 algoritması ile tekrar tarihlerini hesaplayan bir komut satırı uygulamasıdır.

### Temel Kısıtlar
- ✅ **Pure Python** - Sadece standart kütüphane (harici paket YOK)
- ✅ **Dosya Tabanlı Veri** - JSON formatında kalıcı saklama
- ✅ **CLI Arayüz** - Komut satırı menü sistemi
- ❌ **SQL/Veritabanı YOK** - sqlite3 dahil hiçbir SQL kullanılmayacak

---

## 🏗️ Önerilen Klasör Yapısı

```
Bitirme Projesi/
├── main.py                 # Ana giriş noktası ve CLI menüsü
├── storage.py              # JSON okuma/yazma, atomic write
├── auth.py                 # Kayıt/giriş, parola hashleme
├── deck_service.py         # Deck iş mantığı (CRUD)
├── card_service.py         # Kart iş mantığı (CRUD)
├── review_service.py       # SM-2 hesaplama, review kaydı
├── report_service.py       # Raporlama
├── utils.py                # Yardımcı fonksiyonlar, tarih işlemleri
├── data/                   # Veri klasörü
│   ├── users.json
│   ├── decks.json
│   ├── cards.json
│   ├── srs_state.json
│   └── reviews.json
├── tests/                  # Test klasörü
│   └── test_studybuddy.py
├── backups/                # Yedekler (bonus)
└── README.md
```

---

## 📦 Modül Detayları

### 1. `storage.py` - Veri Erişim Katmanı
| Fonksiyon | Açıklama |
|-----------|----------|
| `load_json(filename)` | JSON dosyasını okur |
| `save_json(filename, data)` | Atomic write ile JSON kaydeder |
| `generate_id(collection)` | Benzersiz ID üretir |
| `ensure_data_dir()` | data/ klasörünü oluşturur |

### 2. `auth.py` - Kimlik Doğrulama
| Fonksiyon | Açıklama |
|-----------|----------|
| `hash_password(password)` | Salt + PBKDF2 ile hash |
| `verify_password(password, hash, salt)` | Parola doğrulama |
| `register(email, password)` | Yeni kullanıcı kayıt |
| `login(email, password)` | Giriş ve oturum başlatma |
| `logout()` | Oturum kapatma |

### 3. `deck_service.py` - Deste Yönetimi
| Fonksiyon | Açıklama |
|-----------|----------|
| `create_deck(user_id, name, description)` | Yeni deck oluştur |
| `list_decks(user_id)` | Kullanıcının decklerini listele |
| `update_deck(deck_id, name, description)` | Deck güncelle |
| `delete_deck(deck_id)` | Deck sil (cascade) |

### 4. `card_service.py` - Kart Yönetimi
| Fonksiyon | Açıklama |
|-----------|----------|
| `create_card(deck_id, front, back)` | Yeni kart ekle |
| `list_cards(deck_id)` | Deck'in kartlarını listele |
| `update_card(card_id, front, back)` | Kart güncelle |
| `delete_card(card_id)` | Kart sil |

### 5. `review_service.py` - SM-2 Algoritması
| Fonksiyon | Açıklama |
|-----------|----------|
| `get_due_cards(user_id)` | Bugün due olan kartlar |
| `submit_review(user_id, card_id, quality)` | Review kaydet ve SRS güncelle |
| `calculate_sm2(quality, repetition, ef, interval)` | SM-2 hesaplama |

### 6. `report_service.py` - Raporlama
| Fonksiyon | Açıklama |
|-----------|----------|
| `get_due_count(user_id)` | Bugün due kart sayısı |
| `get_weekly_stats(user_id)` | Son 7 gün istatistikleri |
| `get_deck_stats(deck_id)` | Deck bazlı istatistik |

---

## 🔢 SM-2 Algoritması Formülü

```python
def calculate_sm2(quality, repetition, ef, interval):
    """
    SM-2 benzeri aralıklı tekrar algoritması
    
    Args:
        quality: 0-5 arası kalite puanı
        repetition: Mevcut tekrar sayısı
        ef: Easiness Factor (başlangıç: 2.5)
        interval: Mevcut interval (gün)
    
    Returns:
        (new_repetition, new_ef, new_interval)
    """
    # EF güncelleme
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3
    
    # Kalite < 3 ise sıfırla
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
    
    return new_repetition, new_ef, new_interval
```

---

## 🧪 Test Planı (Minimum 10 Test)

| # | Test Adı | Açıklama |
|---|----------|----------|
| 1 | `test_register_duplicate_email` | Aynı email ile ikinci kayıt engellenir |
| 2 | `test_login_wrong_password` | Yanlış parola reddedilir |
| 3 | `test_deck_crud` | Deck oluştur-listele-güncelle-sil |
| 4 | `test_card_crud` | Kart oluştur-listele-güncelle-sil |
| 5 | `test_review_quality_low` | quality<3: repetition=0, interval=1 |
| 6 | `test_review_quality_high` | quality>=3: interval artar |
| 7 | `test_due_list` | due_date <= today olan kartlar listelenir |
| 8 | `test_user_isolation` | Farklı kullanıcı verileri izole |
| 9 | `test_atomic_write` | JSON dosya bozulmaz |
| 10 | `test_cascade_delete` | Deck silinince kartlar da silinir |

### Testleri Çalıştırma
```bash
python -m unittest discover tests
# veya
python -m unittest tests.test_studybuddy
```

---

## 📅 Geliştirme Takvimi (10 Gün)

| Milestone | Gün | İçerik | Süre |
|-----------|-----|--------|------|
| **M1** | 1-2 | Storage katmanı + JSON yapısı | 2 gün |
| **M2** | 3-4 | Auth (kayıt/giriş) + hashleme | 2 gün |
| **M3** | 5-6 | Deck & Card CRUD + CLI menü | 2 gün |
| **M4** | 7-8 | Review + SM-2 algoritması | 2 gün |
| **M5** | 9 | Raporlama + loglama + yedekleme | 1 gün |
| **M6** | 10 | Testler + README + son düzenleme | 1 gün |

---

## ✅ Kabul Kriterleri

1. ✅ `python main.py` ile uygulama açılıyor
2. ✅ Kayıt + giriş + çıkış çalışıyor
3. ✅ Deck ve kart CRUD tamamen çalışıyor
4. ✅ Review akışı kalite puanı alıp due_date güncelliyor
5. ✅ Bugün due olan kartlar listeleniyor
6. ✅ Veriler dosyaya kaydediliyor (kalıcılık)
7. ✅ Testler çalışıyor: `python -m unittest`
8. ✅ SQL kullanılmıyor (kodda sqlite3 yok)

---

## 🎁 Bonus Özellikler (+10 puan)

- [ ] Yedekleme (shutil ile timestamp'li backup)
- [ ] CSV rapor çıktısı
- [ ] Gelişmiş arama/filtreleme
- [ ] Import özelliği
