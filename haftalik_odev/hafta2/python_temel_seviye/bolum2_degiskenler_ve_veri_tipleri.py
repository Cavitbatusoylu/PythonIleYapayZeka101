# ============================================================
# BÖLÜM 2: Değişkenler ve Veri Tipleri
# ============================================================

# Alıştırma 1: Aşağıdaki bilgileri depolamak için uygun veri tiplerinde 
# değişkenler oluşturun.

# Kendi adınız (string)
ad = "Cavit"

# Doğum yılınız (integer)
dogum_yili = 2000

# Boyunuz metre cinsinden (float)
boy = 1.75

# Öğrenci olup olmadığınız (boolean)
ogrenci_mi = True

# Değişkenlerin tiplerini kontrol edelim
print("Değişken Tipleri:")
print(f"ad: {type(ad)}")
print(f"dogum_yili: {type(dogum_yili)}")
print(f"boy: {type(boy)}")
print(f"ogrenci_mi: {type(ogrenci_mi)}")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 2: Bir önceki alıştırmada oluşturduğunuz değişkenleri kullanarak,
# f-string formatlama yöntemiyle kendinizi tanıtan bir cümleyi ekrana yazdırın.

print(f"Benim adım {ad}, {dogum_yili} yılında doğdum. Boyum {boy} metre ve öğrencilik durumum: {ogrenci_mi}.")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 3: Aşağıdaki veri yapılarını oluşturun:

# En sevdiğiniz üç meyveyi içeren bir liste (list)
favori_meyveler = ["Elma", "Muz", "Çilek"]
print(f"Favori Meyveler (list): {favori_meyveler}")
print(f"Tipi: {type(favori_meyveler)}")

print()

# Marka, model ve yıl bilgilerini içeren bir demet (tuple)
araba_bilgileri = ("Toyota", "Corolla", 2022)
print(f"Araba Bilgileri (tuple): {araba_bilgileri}")
print(f"Tipi: {type(araba_bilgileri)}")

print()

# Bir öğrencinin Matematik, Türkçe ve Fen Bilimleri derslerinden aldığı notları içeren bir küme (set)
ogrenci_notlari = {85, 90, 78}
print(f"Öğrenci Notları (set): {ogrenci_notlari}")
print(f"Tipi: {type(ogrenci_notlari)}")

print()

# Bir kişinin ad, soyad ve sehir bilgilerini anahtar-değer çiftleri olarak tutan bir sözlük (dict)
kisi_bilgileri = {
    "ad": "Cavit",
    "soyad": "Yılmaz",
    "sehir": "İstanbul"
}
print(f"Kişi Bilgileri (dict): {kisi_bilgileri}")
print(f"Tipi: {type(kisi_bilgileri)}")
