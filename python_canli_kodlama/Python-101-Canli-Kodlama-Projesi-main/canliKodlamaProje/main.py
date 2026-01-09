import math

# Anahtar kısımları benzersiz olmalıdır.
ogrenci = {
    "ad": "Ömer",
    "soyad": "Doğan",
    "bölüm": "Bilgisayar Mühendisliği",
    "numara": "02200202020",
    "tc_kimlik": "1231236547841",
}

print("Öğrenci Bölümü : ")
print(ogrenci["bölüm"])


# index = bilgisayar sırası -> 0,1,2,..
# Sıra = Gerçek hayatta insanların kullanmış olduğu sayma sayıları 1,2,3,...
ders_notlari = [75,85,95,45,80]
#                0  1  2  3  4
ders_adlari = ["Matematik","Fizik","Veri Tabanı","Türk Dili Edebiyatı","Web Programlama"]
metin= ders_adlari[1]+ " dersinden " + str(ders_notlari[1]) + " notu girilmiştir."
print(metin)


# max : listede ki en büyük elemanı getirir.
en_yuksek_not = max(ders_notlari)
print(f'En yüksek not : {en_yuksek_not}')
# min : listede ki en küçük elemanı getirir.
en_dusuk_not = min(ders_notlari)
print(f'En düşük not : {en_dusuk_not}')
# sum listedeki tüm elemanların toplamının değerini üretir.
toplam = sum(ders_notlari)
print(f'Ders notları toplamı : {toplam}')

# len : verilen listenin eleman sayısını üretir
eleman_sayisi = len(ders_notlari)
print(f"eleman sayısı : {eleman_sayisi}")
ortalama = toplam / eleman_sayisi
print(ortalama)

harf_notu = None
ders_durumu = None

if ortalama >= 90 and ortalama<=100:
    harf_notu ="AA"
    ders_durumu = "Pekiyi"
elif 85<=ortalama<=89: # ortalama >= 85 and ortalama<=89
    harf_notu = "BA"
    ders_durumu = "İyi- Pekiyi"
elif 80<=ortalama<=84:
    harf_notu = "BB"
    ders_durumu = "İyi"
elif 60<=ortalama<=64:
    harf_notu = "DD"
    ders_durumu = "Geçer"
elif 0<=ortalama<=59:
    harf_notu = "FF"
    ders_durumu = "Kaldı"
elif  65<=ortalama<=79:
    harf_notu = "CC"
    ders_durumu = "Orta"
else:
    print("Lütfen ortalama değerinizi hesaplarken 0 ile 100 arasında notlar giriniz.")


ders_ciktisi = f'Ders Durumu : {ders_durumu}, Harf Notu : {harf_notu}, Derslerin Ortalaması :{ortalama}'
print(ders_ciktisi)