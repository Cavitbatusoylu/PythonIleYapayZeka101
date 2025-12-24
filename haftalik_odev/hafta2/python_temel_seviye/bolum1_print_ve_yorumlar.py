# ============================================================
# BÖLÜM 1: print() Fonksiyonu ve Yorum Satırları
# ============================================================

# Alıştırma 1: Ekrana "Merhaba, Python Dünyası!" yazdıran bir kod yazın.
print("Merhaba, Python Dünyası!")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 2: print() fonksiyonunun sep parametresini kullanarak 
# "Python", "öğrenmek", "çok", "eğlenceli" kelimelerini aralarında 
# - işareti olacak şekilde tek bir satırda yazdırın.
print("Python", "öğrenmek", "çok", "eğlenceli", sep="-")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 3: print() fonksiyonunun end parametresini kullanarak 
# iki farklı print() komutunun çıktısını aynı satırda birleştirin.
print("Adım:", end=" ")
print("Cavit")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 4: Kaçış karakterlerini (\n ve \t) kullanarak 
# aşağıdaki gibi görünen bir çıktıyı tek bir print() fonksiyonu ile oluşturun.
print("Python Dersleri:\n\t- Konu 1\n\t- Konu 2")

print()  # Boş satır

# ------------------------------------------------------------
# Alıştırma 5: Aşağıdaki kod bloğuna, her satırın ne işe yaradığını 
# açıklayan tek satırlık yorumlar ve kodun genel amacını açıklayan 
# çok satırlı bir yorum bloğu ekleyin.

"""
Bu kod bloğu, bir kişinin temel bilgilerini (isim ve yaş) 
değişkenlerde saklayıp ekrana yazdırır.
Basit bir değişken tanımlama ve print fonksiyonu kullanımı örneğidir.
"""

# isim adında bir değişken oluşturulur ve "Ahmet" değeri atanır
isim = "Ahmet"

# yas adında bir değişken oluşturulur ve 25 değeri (tam sayı) atanır
yas = 25

# isim değişkeninin değeri ekrana yazdırılır
print(isim)

# yas değişkeninin değeri ekrana yazdırılır
print(yas)
