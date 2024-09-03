FLO CLTV Prediction

Bu proje, FLO müşterilerinin gelecekteki potansiyel değerlerini tahmin etmek için BG-NBD ve Gamma-Gamma modellerini kullanarak Müşteri Yaşam Boyu Değerini (CLTV) hesaplamayı amaçlamaktadır.
Proje, satış ve pazarlama stratejilerinde yol haritası belirlemek isteyen şirket için uygulanmıştır.

Proje Hakkında

Bu proje kapsamında, FLO'nun OmniChannel müşterilerinin geçmiş alışveriş verileri analiz edilerek, bu müşterilerin gelecekteki alışveriş davranışları ve değerleri tahmin edilmiştir.

Veri Seti

Veri seti, FLO’dan son alışverişlerini 2020 - 2021 yıllarında OmniChannel (hem online hem offline) olarak yapan müşterilerin geçmiş alışveriş davranışlarından oluşmaktadır.
Veri setinde 13 değişken ve 19.945 gözlem bulunmaktadır.

Önemli Değişkenler:

master_id: Eşsiz müşteri numarası

order_channel: Alışveriş yapılan platform (Android, iOS, Desktop, Mobile)

first_order_date: Müşterinin yaptığı ilk alışveriş tarihi

last_order_date: Müşterinin yaptığı son alışveriş tarihi

order_num_total_ever_online: Müşterinin online platformda yaptığı toplam alışveriş sayısı

customer_value_total_ever_online: Müşterinin online alışverişlerinde ödediği toplam ücret


Proje Adımları

1. Veri Hazırlama
 
Veri setindeki aykırı değerler tespit edilip baskılandı.
Müşterilerin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturuldu.
Tarihsel veriler, datetime formatına dönüştürüldü.

3. CLTV Veri Yapısının Oluşturulması

recency, frequency, monetary, ve T değerleri hesaplandı ve yeni bir CLTV veri çerçevesi oluşturuldu.

5. BG/NBD ve Gamma-Gamma Modellerinin Kurulması

BG/NBD modeli kullanılarak müşterilerin satın alma olasılıkları tahmin edildi.
Gamma-Gamma modeli ile müşterilerin ortalama bıraktıkları değer tahmin edildi.
6 aylık CLTV hesaplamaları yapıldı ve en yüksek CLTV değerine sahip 20 müşteri belirlendi.

7. CLTV Değerine Göre Segmentlerin Oluşturulması

Müşteriler, 6 aylık CLTV değerlerine göre 4 segmente ayrıldı.
Her segment için yönetime yönelik aksiyon önerileri geliştirildi.

Sonuçlar

Bu projede elde edilen sonuçlar, FLO'nun müşterilerini daha iyi tanımasına ve onların gelecekteki değerlerini tahmin etmesine olanak tanır. Bu bilgiler, FLO'nun pazarlama ve satış stratejilerini optimize etmek için kullanılabilir.
