import streamlit as st
import numpy as np
import pandas as pd
import pickle
import joblib
import sklearn
from geopy.geocoders import Nominatim, Yandex
from typing import Any, Tuple
geolocator = Yandex(api_key='a3b68fa7-5deb-4262-aaf2-da0d88b205f5')
inv_geolocator = Nominatim(user_agent='sanek052002@gmail.com')


MIN_SQUARE_BY_ROOMS = {
    'студия': 10.0,
    '1': 15.0,
    '2': 26.0,
    '3': 41.5,
    '4': 45.0,
    '5': 80.0,
    '6': 99.5,
    '7': 160.0,
    '8': 211.0,
    '9': 173.7,
    '10 и больше': 332.6,
    'свободная планировка': 19.6}

FEATURES = ['Район', 'Количество_комнат', 'Общая_площадь', 'Ремонт', 'Этаж', 'Этажей_в_доме', 'Тип_дома',
            'Расстояние_до_Краснопресненская', 'Координаты_кластер', 'Метро_1', 'Метро_2', 'Метро_3', 'Общая_площадь_минус_мин',
            'Расстояние_до_Кремля', 'Расстояние_до_Киевская'
            ]


@st.cache_resource
def pickle_load(path):
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model


@st.cache_resource
def joblib_load(path):
    model = joblib.load(path)
    return model


@st.cache_resource
def csv_load(path):
    data = pd.read_csv(path)
    return data


def haversine_distance(lat1: float,
                       lng1: float,
                       lat2: float,
                       lng2: float) -> float:
    """
    Вычисление расстояния между точками по их координатам.

    Параметры
    ----------
    lat1 - широта 1 объекта
    lng1 - долгота 1 объекта
    lat2 - широта 2 объекта
    lng2 - долгота 2 объекта
    """
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    AVG_EARTH_RADIUS = 6371
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = np.sin(
        lat * 0.5)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5)**2
    h = 2 * AVG_EARTH_RADIUS * np.arcsin(np.sqrt(d))
    return h


def accept_user_data() -> Tuple:
    address = st.text_input('Введите адрес квартиры',
                            'Москва улица Тверская 18 к1')
    try:
        location = geolocator.geocode(address)
        st.write('Введенный адрес: ', location)
        lat = location.latitude
        lng = location.longitude
        inv_location = inv_geolocator.reverse((lat, lng), exactly_one=True)
        new_address = inv_location.raw['address']
        suburb = new_address.get('suburb', None)
        if suburb:
            suburb = suburb.replace('район', '').strip()
    except:
        st.error('Невозможно распознать адрес, попробуйте еще раз')

    n_rooms = st.selectbox('Выберите количество комнат', ('студия', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10 и больше',
                                                          'свободная планировка'))

    square = st.number_input('Введите общую площадь квартиры', min_value=8.00)

    repair = st.selectbox('Выберите тип ремонта', ('косметический',
                          'евро', 'требует ремонта', 'дизайнерский'))

    floor = st.select_slider('Выберите этаж', range(1, 100))

    n_floors = st.select_slider(
        'Выберите количество этажей в доме', range(1, 100))

    house_type = st.selectbox('Выберите тип дома', ('панельный',
                              'монолитный', 'кирпичный', 'монолитно-кирпичный', 'блочный'))

    return suburb, n_rooms, square, repair, floor, n_floors, house_type, lat, lng


def prepare_features() -> Tuple[pd.DataFrame, float]:
    suburb, n_rooms, square, repair, floor, n_floors, house_type, lat, lng = accept_user_data()
    kmeans_geo = pickle_load("deploy/models/geo_cluster.pkl")
    stations_encoder = pickle_load("deploy/data/metro_stations.pkl")
    categorical_encoder = joblib_load("deploy/models/categorical_encoder.pkl")
    metros = csv_load("deploy/data/metro_coords.csv")

    dist_krasn = haversine_distance(lat, lng, 55.760378, 37.577114)
    dist_kievskaya = haversine_distance(lat, lng, 55.743117, 37.564132)
    dist_kremlin = haversine_distance(lat, lng, 55.751999, 37.617734)
    coords_cluster = kmeans_geo.predict([[lat, lng]]).item()
    metros['Расстояние'] = haversine_distance(
        lat, lng, metros['Широта'], metros['Долгота'])
    metro_1, metro_2, metro_3 = metros.sort_values(
        by='Расстояние').head(3)['Станция']

    square_munus_min = square-MIN_SQUARE_BY_ROOMS[n_rooms]
    values = [suburb, n_rooms, square, repair, float(floor), float(n_floors), house_type, dist_krasn,
              float(coords_cluster), metro_1, metro_2, metro_3, square_munus_min, dist_kremlin, dist_kievskaya]
    df = pd.DataFrame(dict(zip(FEATURES,values)), index=[0])
    for i in range(1, 4):
        df[f'Метро_{i}'] = stations_encoder.get(df[f'Метро_{i}'].item(), -1)
    df[['Район', 'Количество_комнат', 'Ремонт', 'Тип_дома']] = categorical_encoder.transform(
        df[['Район', 'Количество_комнат', 'Ремонт', 'Тип_дома']])

    return df, square


def predict() -> None:
    data, square = prepare_features()
    predictions = 0
    for fold in range(5):
        model = joblib_load(f'deploy/models/lgb_model_{fold}')
        predictions += model.predict(data)/5

    square_price = int(predictions)//1000
    last_digit = str(predictions)[-1]
    if last_digit == '0':
        value = 'тысяч'
    elif last_digit == '1':
        value = 'тысяча'
    elif last_digit in ['2', '3', '4']:
        value = 'тысячи'
    else:
        value = 'тысяч'

    price = float((predictions*square)/1e6)

    if st.button('Рассчитать цену'):
        st.success(
            f"Стоимость квадратного метра: {square_price} {value} рублей")
        st.success(f"Общая стоимость: {price:.3f} млн. рублей")


def main() -> None:
    st.title('Предсказание цен на вторичное жильё в Москве 🏠')
    st.markdown("""
    * Приложение создано для определения примерной рыночной стоимости квартиры на рынке вторичного жилья в Москве
    * [Github репозиторий](https://github.com/sfnga/Apartment-Price-Prediction)
    """)
    predict()


main()
