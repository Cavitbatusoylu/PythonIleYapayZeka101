# ============================================================
# BÖLÜM 3: Tip Dönüşümleri (Type Casting)
# ============================================================

# Alıştırma 1: Bir string olarak tanımlanmış "1923" değerini integer'a 
# dönüştürün ve üzerine 100 ekleyerek sonucu ekrana yazdırın.

# String olarak tanımlanan değer
yil_string = "1923"
print(f"Orijinal değer (string): {yil_string}")
print(f"Tipi: {type(yil_string)}")

# Integer'a dönüştürme
yil_int = int(yil_string)
print(f"Dönüştürülmüş değer (int): {yil_int}")
print(f"Tipi: {type(yil_int)}")

# 100 ekleme
sonuc = yil_int + 100
print(f"100 eklenmiş hali: {sonuc}")

print()  # Boş satır
print("-" * 50)
print()

# ------------------------------------------------------------
# Alıştırma 2: Kullanıcıdan input() fonksiyonu ile yaşını girmesini isteyen 
# bir program yazın. Kullanıcıdan alınan yaş bilgisini integer'a dönüştürün 
# ve 10 yıl sonra kaç yaşında olacağını hesaplayarak ekrana yazdırın.

# Kullanıcıdan yaş bilgisi alma
yas_string = input("Yaşınızı girin: ")

# String'den integer'a dönüştürme
yas = int(yas_string)

# 10 yıl sonraki yaşı hesaplama
on_yil_sonra = yas + 10

# Sonucu ekrana yazdırma
print(f"Şu anki yaşınız: {yas}")
print(f"10 yıl sonra {on_yil_sonra} yaşında olacaksınız.")
