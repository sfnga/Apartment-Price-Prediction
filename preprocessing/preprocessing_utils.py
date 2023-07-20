import numpy as np
from sklearn.metrics.pairwise import haversine_distances
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent='sanek052002@gmail.com')


def transform_categories(df: pandas.DataFrame, names: list[str]) -> pandas.DataFrame:
    """Создает бинарные признаки, показывающие, содержится
    ли каждое из уникальных значений признака name в строке.
    
    Например, для признака окна с уникальными значениями на_солнечную_сторону, во_двор, на_улицу
    Будет создано 3 бинарных признака Окна_на_солнечную_сторону, Окна_во_двор, Окна_на_улицу
    
    Параметры
    ----------
    df - набор данных
    names - признаки для трансформации
    
    Возвращает
    ----------
    result_df - преобразованный датафрейм
    """
    result_df = df.copy()

    for name in names:
        result_df[name] = result_df[name].astype('category')
        categories = df[name].dropna().unique()

        feature_values = []
        for feat in categories:
            feature_values.extend(feat.split(', '))
        feature_values = set(feature_values)

        for feat in feature_values:
            result_df[f"{name}_{feat.replace(' ','_')}"] = result_df[
                name].apply(lambda x: feat in x).astype(float)

        result_df = result_df.drop(columns=name)
    return result_df


def correct_ceil(x: float) -> float:
    """
    Функция для корректировки высоты потолков.
    """
    # для высоты в миллиметрах
    if x > 2200:
        x /= 1000
    # для высоты в сантиметрах
    elif x > 210:
        x /= 100
    # для высоты в дециметрах
    elif x > 20 and x < 75:
        x /= 10
    # высоту меньше 1м заполняем nan
    elif x < 1:
        x = np.nan
    return x


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


def extract_address_from_coords(row: object) -> object:
    """Функция для получения города и района по координатам."""
    coords = f"{row['Широта']}, {row['Долгота']}"
    location = geolocator.reverse(coords, exactly_one=True)
    address = location.raw['address']

    city_district = address.get('suburb', np.nan)
    city = address.get('city', np.nan)

    row['Район'] = city_district
    row['Город'] = city
    return row
