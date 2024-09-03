# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 13:37:18 2024

@author: oem
"""

! pip install lifetimes
import pandas as pd
import datetime as dt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)  
pd.set_option('display.max_colwidth', None)

df = pd.read_csv("flo_data_20k.csv")
df_copy = df.copy()

#Aykırı değerleri baskılamak için gerekli olan outlier_thresholdsve replace_with_thresholdsfonksiyonlarını tanımlayınız. 
def outlier_thresholdsve(dataframe, variable) :
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3-quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit
def replace_with_thresholds(dataframe, variable) :
    low_limit, up_limit = outlier_thresholdsve(dataframe, variable)
    dataframe.loc[(dataframe[variable]> up_limit), variable] = up_limit

df.describe().T
# "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", "customer_value_total_ever_online" değişkenlerinin aykırı değerleri varsa baskılayanız
columns = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", 
"customer_value_total_ever_online"]
for col in columns :
    replace_with_thresholds(df, col)
# Omnichannel müşterilerin hem online'dan hem de offline platformlardan alışveriş yaptığını ifade etmektedir. 
#Her bir müşterinin toplamalışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# Değişkentiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz
df.info()
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)

# Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi olarak alınız
df["last_order_date"].max() #2021-05-30
analysis_date = dt.datetime(2021,6,1)

# customer_id, recency_cltv_weekly, T_weekly, frequency ve monetary_cltv_avg değerlerinin yer aldığı yeni bir cltv dataframe'i oluşturunuz.
cltv_df = pd.DataFrame()
cltv_df["customer_id"] = df["master_id"]
cltv_df["recency_cltv_weekly"] = ((df["last_order_date"] - df["first_order_date"]).dt.days) / 7
cltv_df["T_weekly"] = ((analysis_date - df["first_order_date"]).dt.days) / 7
cltv_df["frequency"] = df["order_num_total"]
cltv_df["monetary_cltv_avg"] = df["customer_value_total"] / df["order_num_total"]
cltv_df.head()

#BG/NBD modelinifit ediniz.
# • 3 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_3_month olarak cltvdataframe'ine ekleyiniz.
# • 6 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_6_month olarak cltvdataframe'ine ekleyiniz
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df["frequency"],
cltv_df["recency_cltv_weekly"],
cltv_df["T_weekly"])
cltv_df["exp_sales_3_month"] = bgf.predict(4*3,
                                          cltv_df["frequency"],
                                          cltv_df["recency_cltv_weekly"],
                                          cltv_df["T_weekly"])
cltv_df["exp_sales_6_month"] = bgf.predict(4*6,
                                          cltv_df["frequency"],
                                          cltv_df["recency_cltv_weekly"],
                                          cltv_df["T_weekly"])
cltv_df[["exp_sales_6_month","exp_sales_3_month"]]

# Gamma-Gamma modelinifit ediniz. Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltvdataframe'ine ekleyiniz.
ggf = GammaGammaFitter(penalizer_coef=0.01)
cltv_df["frequency"] = cltv_df["frequency"].astype(int)
ggf.fit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])
cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])
cltv_df.head()

#6 aylık CLTV hesaplayınız ve cltv ismiyle dataframe'e ekleyiniz. 
#Cltvdeğeri enyüksek20 kişiyi gözlemleyiniz
cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df["frequency"],
                                   cltv_df["recency_cltv_weekly"],
                                   cltv_df["T_weekly"],
                                   cltv_df["monetary_cltv_avg"],
                                   time = 6 ,
                                   freq = "W",
                                   discount_rate = 0.01)
cltv_df["cltv"] = cltv
cltv.head(20)

# 6 aylık CLTV'ye göre tüm müşterilerinizi 4 gruba (segmente) ayırınız ve grup isimlerini veri setine ekleyiniz.
cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
cltv_df.head()

#Tüm süreci fonksiyonlaştırı.
def create_cltv_df(DataFrame) :
    columns = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", 
    "customer_value_total_ever_online"]
    for col in columns :
        replace_with_thresholds(df, col)
    # Omnichannel müşterilerin hem online'dan hem de offline platformlardan alışveriş yaptığını ifade etmektedir. 
    #Her bir müşterinin toplamalışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz
    df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

    # Değişkentiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz
    df.info()
    date_columns = df.columns[df.columns.str.contains("date")]
    df[date_columns] = df[date_columns].apply(pd.to_datetime)

    # Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi olarak alınız
    df["last_order_date"].max() #2021-05-30
    analysis_date = dt.datetime(2021,6,1)

    # customer_id, recency_cltv_weekly, T_weekly, frequency ve monetary_cltv_avg değerlerinin yer aldığı yeni bir cltv dataframe'i oluşturunuz.
    cltv_df = pd.DataFrame()
    cltv_df["customer_id"] = df["master_id"]
    cltv_df["recency_cltv_weekly"] = ((df["last_order_date"] - df["first_order_date"]).dt.days) / 7
    cltv_df["T_weekly"] = ((analysis_date - df["first_order_date"]).dt.days) / 7
    cltv_df["frequency"] = df["order_num_total"]
    cltv_df["monetary_cltv_avg"] = df["customer_value_total"] / df["order_num_total"]
    cltv_df.head()

    #BG/NBD modelinifit ediniz.
    # • 3 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_3_month olarak cltvdataframe'ine ekleyiniz.
    # • 6 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_6_month olarak cltvdataframe'ine ekleyiniz
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df["frequency"],
    cltv_df["recency_cltv_weekly"],
    cltv_df["T_weekly"])
    cltv_df["exp_sales_3_month"] = bgf.predict(4*3,
                                              cltv_df["frequency"],
                                              cltv_df["recency_cltv_weekly"],
                                              cltv_df["T_weekly"])
    cltv_df["exp_sales_6_month"] = bgf.predict(4*6,
                                              cltv_df["frequency"],
                                              cltv_df["recency_cltv_weekly"],
                                              cltv_df["T_weekly"])
    cltv_df[["exp_sales_6_month","exp_sales_3_month"]]

    # Gamma-Gamma modelinifit ediniz. Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltvdataframe'ine ekleyiniz.
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    cltv_df["frequency"] = cltv_df["frequency"].astype(int)
    ggf.fit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])
    cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])
    cltv_df.head()

    #6 aylık CLTV hesaplayınız ve cltv ismiyle dataframe'e ekleyiniz. 
    #Cltvdeğeri enyüksek20 kişiyi gözlemleyiniz
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df["frequency"],
                                       cltv_df["recency_cltv_weekly"],
                                       cltv_df["T_weekly"],
                                       cltv_df["monetary_cltv_avg"],
                                       time = 6 ,
                                       freq = "W",
                                       discount_rate = 0.01)
    cltv_df["cltv"] = cltv
    cltv.head(20)

    # 6 aylık CLTV'ye göre tüm müşterilerinizi 4 gruba (segmente) ayırınız ve grup isimlerini veri setine ekleyiniz.
    cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
    cltv_df.head()
    
    return cltv_df

cltv_df = create_cltv_df(df)
cltv_df.head(10)

    