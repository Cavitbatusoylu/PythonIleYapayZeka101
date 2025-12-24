# ============================================================
# BÖLÜM 5: math Modülü ve Dahili Fonksiyonlar
# ============================================================

# math modülünü programımıza dahil ediyoruz
import math

# Alıştırma 1: Yarıçapı 7 olan bir dairenin alanını (Alan = π * r^2) ve 
# çevresini (Çevre = 2 * π * r) math.pi sabitini ve math.pow() fonksiyonunu 
# kullanarak hesaplayın. Sonuçları ekrana yazdırın.

print("=" * 50)
print("Alıştırma 1: Daire Hesaplamaları")
print("=" * 50)

# Yarıçap değeri
yaricap = 7

print(f"Yarıçap (r): {yaricap}")
print(f"π (Pi) sayısı: {math.pi}")
print()

# Alan hesaplama: π * r^2
# math.pow(taban, üs) fonksiyonu üs alma işlemi yapar
alan = math.pi * math.pow(yaricap, 2)
print(f"Dairenin Alanı (π * r²): {alan:.2f}")

# Çevre hesaplama: 2 * π * r
cevre = 2 * math.pi * yaricap
print(f"Dairenin Çevresi (2 * π * r): {cevre:.2f}")

print()
print("-" * 50)
print()

# ------------------------------------------------------------
# Alıştırma 2: [15, 4, 27, 13, 32, 8] sayılarından oluşan bir listenin 
# en büyük ve en küçük elemanını max() ve min() fonksiyonları ile bulun. 
# Ayrıca listedeki tüm sayıların toplamını sum() fonksiyonu ile hesaplayın. 
# Sonuçları ekrana yazdırın.

print("=" * 50)
print("Alıştırma 2: Dahili Fonksiyonlar (max, min, sum)")
print("=" * 50)

# Sayı listesi
sayilar = [15, 4, 27, 13, 32, 8]

print(f"Sayı Listesi: {sayilar}")
print()

# En büyük elemanı bulma
en_buyuk = max(sayilar)
print(f"En büyük eleman (max): {en_buyuk}")

# En küçük elemanı bulma
en_kucuk = min(sayilar)
print(f"En küçük eleman (min): {en_kucuk}")

# Tüm sayıların toplamını hesaplama
toplam = sum(sayilar)
print(f"Tüm sayıların toplamı (sum): {toplam}")

# Bonus: Ortalama hesaplama
ortalama = toplam / len(sayilar)
print(f"Sayıların ortalaması: {ortalama:.2f}")
