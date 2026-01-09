from business import *

ogrenci = {
    "ad": "Ömer",
    "soyad": "Doğan",
    "bölüm": "Bilgisayar Mühendisliği",
    "numara": "02200202020",
    "tc_kimlik": "1231236547841",
}


# SOLID -
# Single Responsibility
# Open Closed

dersler = [
    {'ders': 'Matematik', 'puan': 75},
    {'ders': 'Fizik', 'puan': 85},
    {'ders': 'Veri Tabanı', 'puan': 95},
    {'ders': 'Fizik', 'puan': 85},
    {'ders': 'Türk Dili Edebiyatı', 'puan': 45},
    {'ders': 'Web Programlama', 'puan': 80},
]


# ortalama , en yüksek not , en düşük not hesaplamaları yapılacak.

max_not = en_yuksek_not(dersler)
min_not = en_dusuk_not(dersler)
ortalama = ortalama_hesaplama(dersler)

istatistik_yazdirma(en_buyuk=max_not, en_kucuk=min_not, ortalama=ortalama)

sonuc = harf_notu_ve_ders_durumu_bilgileri(ortalama)
print(f'Ders durumu: {sonuc[0]}')
print(f'Harf Notu: {sonuc[1]}')
