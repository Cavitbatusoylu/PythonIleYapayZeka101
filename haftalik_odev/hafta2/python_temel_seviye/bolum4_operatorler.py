# ============================================================
# BÖLÜM 4: Operatörler
# ============================================================

# Alıştırma 1: İki sayı değişkeni oluşturun (sayi1 = 50, sayi2 = 15). 
# Bu iki sayının toplamını, farkını, çarpımını ve bölümünü hesaplayıp 
# sonuçları açıklayıcı metinlerle birlikte ekrana yazdırın.

print("=" * 50)
print("Alıştırma 1: Matematiksel Operatörler")
print("=" * 50)

sayi1 = 50
sayi2 = 15

print(f"Birinci sayı: {sayi1}")
print(f"İkinci sayı: {sayi2}")
print()

# Toplama işlemi
toplam = sayi1 + sayi2
print(f"Toplam ({sayi1} + {sayi2}): {toplam}")

# Çıkarma işlemi
fark = sayi1 - sayi2
print(f"Fark ({sayi1} - {sayi2}): {fark}")

# Çarpma işlemi
carpim = sayi1 * sayi2
print(f"Çarpım ({sayi1} * {sayi2}): {carpim}")

# Bölme işlemi
bolum = sayi1 / sayi2
print(f"Bölüm ({sayi1} / {sayi2}): {bolum}")

print()
print("-" * 50)
print()

# ------------------------------------------------------------
# Alıştırma 2: Kullanıcıdan bir sayı girmesini isteyin. 
# Girilen sayının 100'den büyük olup olmadığını, 100'e eşit olup olmadığını 
# ve 100'den küçük olup olmadığını karşılaştırma operatörleri kullanarak 
# kontrol edin ve sonuçları (True veya False) ekrana yazdırın.

print("=" * 50)
print("Alıştırma 2: Karşılaştırma Operatörleri")
print("=" * 50)

# Kullanıcıdan sayı alma
girilen_sayi = int(input("Bir sayı girin: "))

print(f"\nGirilen sayı: {girilen_sayi}")
print()

# Karşılaştırma işlemleri
buyuk_mu = girilen_sayi > 100
print(f"{girilen_sayi} > 100 (100'den büyük mü?): {buyuk_mu}")

esit_mi = girilen_sayi == 100
print(f"{girilen_sayi} == 100 (100'e eşit mi?): {esit_mi}")

kucuk_mu = girilen_sayi < 100
print(f"{girilen_sayi} < 100 (100'den küçük mü?): {kucuk_mu}")

print()
print("-" * 50)
print()

# ------------------------------------------------------------
# Alıştırma 3: Bir kullanıcının bir sisteme giriş yapabilmesi için 
# kullanıcı adının "admin" ve şifresinin "12345" olması gerektiğini varsayalım. 
# Mantıksal operatörler (and) kullanarak bu iki koşulun aynı anda sağlanıp 
# sağlanmadığını kontrol eden bir ifade yazın ve sonucunu ekrana yazdırın.

print("=" * 50)
print("Alıştırma 3: Mantıksal Operatörler")
print("=" * 50)

# Doğru kullanıcı adı ve şifre
dogru_kullanici_adi = "admin"
dogru_sifre = "12345"

# Kullanıcıdan giriş bilgilerini alma
kullanici_adi = input("Kullanıcı adı girin: ")
sifre = input("Şifre girin: ")

# Mantıksal operatör (and) ile kontrol
giris_basarili = (kullanici_adi == dogru_kullanici_adi) and (sifre == dogru_sifre)

print()
print(f"Kullanıcı adı doğru mu?: {kullanici_adi == dogru_kullanici_adi}")
print(f"Şifre doğru mu?: {sifre == dogru_sifre}")
print(f"Giriş başarılı mı? (her iki koşul da sağlanıyor mu?): {giris_basarili}")

if giris_basarili:
    print("\n✓ Sisteme giriş başarılı!")
else:
    print("\n✗ Giriş başarısız! Kullanıcı adı veya şifre hatalı.")
