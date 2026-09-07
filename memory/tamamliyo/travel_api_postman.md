# Tamamliyo Travel API v3 (Postman collection)

## GET ürün kodları
https://api.tamamliyo.com/partner/v3/seyahat-saglik-sigortasi/urun-kodlari
HEADERS: token: 

## POST fiyat al
{{api}}/partner/v3/seyahat-saglik-sigortasi/fiyat-al
HEADERS: token:  | token: 
REQUEST:
{
    "sigortaliSayisi" : 1,
    "baslangicTarihi": "2024-08-20",
    "bitisTarihi": "2024-08-21",
    "urun" : "yurtdisi-seyahat"
}

## POST teklif olustur
{{api}}/partner/v3/seyahat-saglik-sigortasi/teklif-olustur
HEADERS: token:  | Accept: application/json
REQUEST:
{
    "sigortaEttiren": {
            "tcKimlikNo": "12xxx",
            "dogumTarihi": "2000-03-18"
    },
    "sigortali": [
        {
            "tcKimlikNo": "12xxx",
            "dogumTarihi": "1999-03-18"
        },
        {
            //Birden fazla kişi olursa eklenecek
            "tcKimlikNo": "44xxx",
            "dogumTarihi": "2000-04-19"
        }
    ],
    "baslangicTarihi": "2024-08-22",
    "bitisTarihi": "2024-08-23",
    "email": "bilgi@tamamliyo.com",
    "gsmNo": "555xxx",
    "urun" : "yurtdisi-seyahat",
    "ulkeKodu":"300"
    //"urun" : "yurtici-seyahat",
    //"ilKodu": 35


}
RESPONSE ORNEGI:
{
    "success": true,
    "data": {
        "teklifBilgileri": {
            "fiyat": "13,00 ₺",
            "fiyatUsd": "0.39",
            "fiyatEuro": "0.36",
            "teklifId": 58503,
            "olusturulmaTarihi": "2024-07-15 14:33:19"
        },
        "urunBilgileri": {
            "urunId": 177,
            "urunAdi": "Seyahat Destek Hizmet Paketi",
            "urunAdiMultiple": {
                "tr": "Seyahat Destek Hizmet Paketi",
                "en": "Travel Support Service Package",
                "ru": "Пакет услуг по сопровождению путешествий"
            },
            "urunTanimi": "Seyahat Destek Hizmet Paketi",
            "urunKategoriBaslik": "Seyahat Destek Hizmet Paketi",
            "urunKategoriAciklama": "Seyahat Destek Hizmet Paketi ile yurt içi seyahatlerinizde beklenmedik sağlık sorunları durumunda tıbbi müdahalelerde geçerlidir.",
            "teminatlar": {
                "tr": {
                    "Sadece yurt içi seyahatlerde geçerli": "",
                    "Online doktor hizmeti": "",
                    "5 saatten fazla rötarlarda rötar destek hizmeti": "",
                    "Ani gelişen sağlık durumlarında tıbbi müdahale": "",
                    "Anlaşmalı hastanelerde muayene indirimi": ""
                },
                "en": {
                    "Valid only for domestic travel": "",
                    "Online doctor service": "",
                    "Delay support for delays over 5 hours": "",
                    "Medical intervention in case of sudden health conditions": "",
                    "Discount on examinations at contracted hospitals": ""
                },
                "ru": {
                    "Действительно только для внутренних поездок": "",
                    "Услуга онлайн-врача": "",
                    "Поддержка при задержках более 5 часов": "",
                    "Медицинское вмешательство при внезапных проблемах со здоровьем": "",
                    "Скидка на осмотры в аккредитованных больницах": ""
                }
            }
        },
        "kisiselBilgiler": {
            "ad": "TEST",
            "soyad": "TEST",
            "tcKimlikNo": "12xxx",
            "dogumTarihi": "1999-03-18",
            "cinsiyet": "E",
            "gsmNo": "542xxx",
            "email": "bilgi@tamamliyo.com"
        },
        "sigortaSirketiBilgileri": {
            "sigortaSirketiId": 11,
            "kisaAdi": "Tamamliyo",
            "tamAdi": "Tamamliyo",
            "yayinci": "Seyahat Destek Hizmet Paketi ,Tamamliyo teknoloji tarafında sunulmaktadır."
        }
    },
    "dataMulti": [
        {
            "teklifBilgileri": {
                "fiyat": "13,00 ₺",
                "fiyatUsd": "0.39",
                "fiyatEuro": "0.36",
                "teklifId": 58503,
                "olusturulmaTarihi": "2024-07-15 14:33:19"
            },
            "urunBilgileri": {
                "urunId": 177,
                "urunAdi": "Seyahat Destek Hizmet Pak

## POST odeme yap
{{api}}/partner/v3/seyahat-saglik-sigortasi/odeme-yap
HEADERS: token:  | Accept: application/json
REQUEST:
{
    "odemeTipi" : "2",
    "teklifId" : "766787",
    "krediKartiCvv" : "000",
    "krediKartiNo" : "1234123412341234",
    "krediKartiBitisTarihi" : "2028-12-01",
    "krediKartiAd" : "test",
    "krediKartiSoyad" : "test",
    "ilId" : 34,
    "ilceId" : "1",
    "adres" : "test adresimm"
}

## POST Cari Ödeme Onay
{{api}}/partner/v3/seyahat-saglik-sigortasi/odeme-onay
HEADERS: Content-Type: application/json | token: 
REQUEST:
{
    // Açık Tahsilat Endpoint

    "status_code" : 100,
    "payment_status" : "Payment Successfully Completed",
    "teklifId" : 58510,
    "parameters": {
        "pnrNo": "A1B2C3",
        "flightNumber": "AA1234",
        "ticketNumber": "12345678",
        "company" : "KamilKoç",
        "arrivalLocation" : "İzmir",
        "departureLocation" : "Ankara",
        "ticketType" : "0",
        "departureDateTime" : "2024-07-20"
    }
}

## POST police olustur
{{api}}/partner/v3/seyahat-saglik-sigortasi/police-olustur
HEADERS: token:  | Accept: application/json
REQUEST:
{
    "teklifId" : "766787"
}

## POST makbuz-pdf
https://api-test.tamamliyo.com/partner/v3/seyahat-saglik-sigortasi/makbuz-pdf
HEADERS: token: 
REQUEST:
{
    "sigortaEttiren": {
            "tcKimlikNo": "14993697604",
            "dogumTarihi": "2001-03-17"
    },
    "sigortali": [
        {
            "tcKimlikNo": "14993697604",
            "dogumTarihi": "2001-03-17",
            "relationTypeId" : "F"
        }
    ],
    "baslangicTarihi": "2022-11-12",
    "bitisTarihi": "2022-12-20",
    "email": "bilgi@tamamliyo.com",
    "gsmNo": "5448202338",
    "urunKodu" : 4,
    "teklifId" : 14866
}

## POST police-pdf
{{api}}/partner/v3/seyahat-saglik-sigortasi/police-pdf
HEADERS: token: 
REQUEST:
{
    "teklifId" : 780697
}

## POST ilceler
https://api-test.tamamliyo.com/partner/v1/ilceler
HEADERS: token: 
REQUEST:
{
    "ilId" : 34
}

## POST teklif bilgileri
{{apitest}}/partner/v3/seyahat-saglik-sigortasi/teklif-bilgileri
HEADERS: token: 
REQUEST:
{
    "teklifId":58485
}