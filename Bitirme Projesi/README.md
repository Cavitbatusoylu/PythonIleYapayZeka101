# 📚 StudyBuddy - Aralıklı Tekrar Sistemi

**Techcareer.net Python ile Yapay Zeka Eğitimi Bitirme Projesi**

StudyBuddy, flashcard tabanlı bir çalışma ve aralıklı tekrar (spaced repetition) sistemidir. SM-2 algoritması kullanarak öğrenme sürecinizi optimize eder.

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Harici kütüphane gerekmez (Pure Python)

### Başlatma
```bash
cd "Bitirme Projesi"
python main.py
```

---

## 📋 Özellikler

### ✅ Temel Özellikler
- **Kullanıcı Yönetimi:** Kayıt, giriş, çıkış
- **Deck Yönetimi:** Deste oluştur, listele, güncelle, sil
- **Kart Yönetimi:** Flashcard ekle, listele, güncelle, sil
- **Çalışma Akışı:** Kartları çalış, 0-5 puan ver
- **Aralıklı Tekrar:** SM-2 algoritması ile tekrar zamanlaması
- **Raporlama:** Bugün due kartlar, haftalık istatistikler

### 🎁 Bonus Özellikler
- ✅ Yedekleme (timestamp ile)
- ✅ CSV dışa aktarma
- ✅ CSV içe aktarma (import)
- ✅ Gelişmiş kart arama
- ✅ Deck'e göre filtreleme

---

## 🎮 Kullanım

### Ana Menü
```
=== StudyBuddy ===
1) Kayıt / Giriş
2) Deck İşlemleri
3) Kart İşlemleri
4) Bugün Çalış
5) Raporlar
6) Arama
7) Yedekleme & Import
8) Çıkış
Seçiminiz:
```

### Çalışma Akışı Örneği
```
Kart #1: HTTP nedir?
Cevap gösterilsin mi? (E/H): E
Cevap: Hypertext Transfer Protocol...

Kalite puanı (0-5):
  0: Hiç hatırlamadım
  1: Çok zor hatırladım
  2: Kısmen hatırladım
  3: Doğru ama zor
  4: Doğru ve rahat
  5: Mükemmel
Puanınız: 4

✓ Güncellendi! Sonraki tekrar: 2026-01-15
```

---

## 📁 Veri Formatı

Veriler `data/` klasöründe JSON formatında saklanır:

### users.json
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "password_hash": "...",
    "salt": "...",
    "created_at": "2026-01-09T10:00:00"
  }
]
```

### decks.json
```json
[
  {
    "id": 10,
    "user_id": 1,
    "name": "Python Temelleri",
    "description": "Python kavramları"
  }
]
```

### cards.json
```json
[
  {
    "id": 100,
    "deck_id": 10,
    "front": "List nedir?",
    "back": "Sıralı, değiştirilebilir koleksiyon",
    "created_at": "2026-01-09T10:05:00"
  }
]
```

### srs_state.json
```json
[
  {
    "id": 1000,
    "user_id": 1,
    "card_id": 100,
    "repetition": 2,
    "interval_days": 6,
    "ef": 2.36,
    "due_date": "2026-01-15",
    "last_quality": 4
  }
]
```

### reviews.json
```json
[
  {
    "id": 5000,
    "user_id": 1,
    "card_id": 100,
    "quality": 4,
    "reviewed_at": "2026-01-09T10:10:00"
  }
]
```

---

## 🧪 Testler

### Testleri Çalıştırma
```bash
python -m unittest discover tests
```

### Test Kapsamı
- Kayıt/Giriş doğrulama
- Deck CRUD işlemleri
- Kart CRUD işlemleri
- SM-2 algoritması hesaplamaları
- Kullanıcı veri izolasyonu
- Cascade silme

---

## 🏗️ Proje Yapısı

```
Bitirme Projesi/
├── main.py              # Ana giriş ve CLI menüsü
├── storage.py           # JSON okuma/yazma
├── auth.py              # Kimlik doğrulama
├── deck_service.py      # Deck işlemleri
├── card_service.py      # Kart işlemleri
├── review_service.py    # SM-2 ve review
├── report_service.py    # Raporlama
├── backup_service.py    # Yedekleme ve import
├── cli_handlers.py      # CLI akış yöneticileri
├── utils.py             # Yardımcı fonksiyonlar
├── data/                # Veri dosyaları
├── tests/               # Unit testler (18 adet)
├── backups/             # Yedekler
└── README.md
```

---

## 📖 SM-2 Algoritması

Kalite puanına göre:
- **0-2:** Kart sıfırlanır, yarın tekrar
- **3-5:** Interval artar (1 → 6 → EF ile çarpım)

EF (Easiness Factor) formülü:
```
EF = EF + (0.1 - (5-q) * (0.08 + (5-q)*0.02))
EF minimum 1.3
```

---

## 👤 Geliştirici

**Cavit Batusoylu**  
Techcareer.net Python ile Yapay Zeka Eğitimi

---

## 📜 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
