
def en_yuksek_not(lessons):
    puanlar = []
    for lesson in lessons:
        puanlar.append(lesson['puan'])
    en_buyuk = max(puanlar)

    return en_buyuk


def en_dusuk_not(lessons):
    puanlar = []
    for lesson in lessons:
        puanlar.append(lesson['puan'])

    en_kucuk = min(puanlar)
    return en_kucuk

def ortalama_hesaplama(lessons):

    puanlar = []
    for lesson in lessons:
        puanlar.append(lesson['puan'])

    toplam = sum(puanlar)
    eleman_sayisi = len(puanlar)
    ortalama = toplam / eleman_sayisi
    return ortalama


def istatistik_yazdirma(ortalama,en_kucuk,en_buyuk):
    print(f'Ortalama : {ortalama}, En düşük Not : {en_kucuk}, En Büyük Not : {en_buyuk}')

# tanımlama
# f(x) = 2x +5

# f(1), f(2), f(-25)
def harf_notu_ve_ders_durumu_bilgileri(average):
    harf_notu = None
    ders_durumu = None

    if average >= 90 and average <= 100:
        harf_notu = "AA"
        ders_durumu = "Pekiyi"
    elif 85 <= average <= 89:  # ortalama >= 85 and ortalama<=89
        harf_notu = "BA"
        ders_durumu = "İyi- Pekiyi"
    elif 80 <= average <= 84:
        harf_notu = "BB"
        ders_durumu = "İyi"
    elif 60 <= average <= 64:
        harf_notu = "DD"
        ders_durumu = "Geçer"
    elif 0 <= average <= 59:
        harf_notu = "FF"
        ders_durumu = "Kaldı"
    elif 65 <= average <= 79:
        harf_notu = "CC"
        ders_durumu = "Orta"
    else:
        print("Lütfen ortalama değerinizi hesaplarken 0 ile 100 arasında notlar giriniz.")

    return ders_durumu, harf_notu