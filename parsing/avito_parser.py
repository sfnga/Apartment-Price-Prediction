import requests
import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_
from bs4 import BeautifulSoup
from urllib.parse import unquote
from datetime import timedelta, date
import re
import time
import sqlite3


CIPHERS = """ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"""
months = {
    'декабря': '12',
    'ноября': '11',
    'октября': '10',
    'сентября': '9',
    'августа': '8',
    'июля': '07',
    'июня': '06',
    'мая': '05',
    'апреля': '04',
    'марта': '03',
    'февраля': '02',
    'января': '01',
}


class TlsAdapter(HTTPAdapter):

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(
            ciphers=CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(
            *pool_args, ssl_context=ctx, **pool_kwargs)


session = requests.session()
adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
session.mount("https://", adapter)


def get_links(url, page=1):
    """Функция для получения ссылок на все объявления со страницы."""
    try:
        # ссылка на страницу
        url = url+f"&p={page}&s=104"
        r = session.request('GET', url)
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.find_all("a", {"data-marker": "item-title"})
        # добавляем ссылки на объявления со страницы
        links = []
        for item in items:
            links.append(f'https://avito.ru/{item["href"]}')
        return links
    except:
        print("failed to get link")
        return


def get_advertisements(url, start_page=1, end_page=101):
    """Функция для получения информации об объявлениях.

    Параметры
    ----------
    url - ссылка на запрос
    start_page - страница, начиная с которой нужно просматривать объявления
    end_page - страница, заканчивая которой нужно просматривать объявления
    """
    # проходим по страницам
    for page in range(start_page, end_page):
        # получаем ссылки на объявления со страницы
        links = get_links(url, page=page)
        if not links:
            print(f"{page} error")
            continue
        # для каждого объявления добавляем информацию
        for link in links:
            get_appartments_info(link)
            time.sleep(5)
        print(f"{page} done")
        time.sleep(30)


def insert_into_database(offer):
    """Добавление объявления в базу данных."""
    offer_id = offer['ID']
    connection = sqlite3.connect('houseprices.db')
    cursor = connection.cursor()
    cursor.execute("""
            SELECT ID FROM houseprices
            WHERE ID= (?)
            """, (offer_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("""
            INSERT INTO houseprices
            VALUES(:ID, :Ссылка, :Цена, :Дата, :Адрес, :Этаж, :Количество_комнат, :Балкон_или_лоджия,
                   :Тип_комнат, :Общая_площадь, :Жилая_площадь, :Площадь_кухни, :Высота_потолков,
                   :Санузел, :Окна, :Ремонт, :Мебель, :Тёплый_пол, :Отделка, :Техника, :Способ_продажи,
                   :Вид_сделки, :Тип_дома, :В_доме, :Год_постройки, :Этажей_в_доме,
                   :Пассажирский_лифт, :Грузовой_лифт, :Парковка, :Двор, :Название_новостройки,
                   :Корпус_строение, :Официальный_застройщик, :Тип_участия, :Срок_сдачи, :Метро_1,
                   :Метро_2, :Метро_3, :Расстояние_до_метро_1, :Расстояние_до_метро_2,
                   :Расстояние_до_метро_3, :Широта, :Долгота, :Запланирован_снос  
                   )""", offer)
        connection.commit()
        print(f"Добавлено {offer['Ссылка']}")
    connection.close()


def get_appartments_info(link):
    """Получение информации о квартире."""

    characteristics = {
        'ID': None,
        'Ссылка': None,
        'Цена': None,
        'Дата': None,
        'Адрес': None,

        'Этаж': None,
        'Количество_комнат': None,
        'Балкон_или_лоджия': None,
        'Тип_комнат': None,
        'Общая_площадь': None,
        'Жилая_площадь': None,
        'Площадь_кухни': None,
        'Высота_потолков': None,
        'Санузел': None,
        'Окна': None,
        'Ремонт': None,
        'Мебель': None,
        'Тёплый_пол': None,
        'Отделка': None,
        'Техника': None,
        'Способ_продажи': None,
        'Вид_сделки': None,

        'Тип_дома': None,
        'В_доме': None,
        'Год_постройки': None,
        'Этажей_в_доме': None,
        'Пассажирский_лифт': None,
        'Грузовой_лифт': None,
        'Парковка': None,
        'Двор': None,

        'Название_новостройки': None,
        'Корпус_строение': None,
        'Официальный_застройщик': None,
        'Тип_участия': None,
        'Срок_сдачи': None,

        'Метро_1': None,
        'Метро_2': None,
        'Метро_3': None,
        'Расстояние_до_метро_1': None,
        'Расстояние_до_метро_2': None,
        'Расстояние_до_метро_3': None,
        'Широта': None,
        'Долгота': None,
        'Запланирован_снос': None
    }
    try:
        r = session.request('GET', link)
        soup = BeautifulSoup(r.text, "lxml")
        # цена
        price = soup.find("meta", {"property": "product:price:amount"})[
            'content']
        characteristics['Цена'] = price
    except:
        print(f"{link} error in price")
        return

    try:
        # Ссылка на объявление
        characteristics['Ссылка'] = link

        # ID объявления для отслеживания дубликатов
        characteristics['ID'] = link.split('_')[-1]

        # Дата публикации
        """
        пример даты объявления:
        3 января в 19:39
        """
        date_ = soup.find(
            "span", {"data-marker": re.compile('item-view/item-date')}).get_text()
        if 'сегодня' in date_:
            date_ = f"{date.today():%Y-%m-%d}"
        elif 'вчера' in date_:
            date_ = f"{date.today()-timedelta(days=1):%Y-%m-%d}"
        else:
            day = re.search('[0-9]+', date_)[0]
            if len(day) == 1:
                day = '0'+day

            for m in months:
                if m in date_:
                    month = months[m]
                    break
            if month in ['01', '02']:
                year = '2023'
            else:
                year = '2022'
            date_ = year+'-'+month+'-'+day

        characteristics['Дата'] = date_
        # адрес
        address = soup.find(class_=re.compile(
            'style-item-address__string')).get_text()
        characteristics['Адрес'] = address

        # о квартире
        appartment = soup.find_all(
            class_=re.compile("params-paramsList__item"))
        for item in appartment:
            item = item.get_text().split(": ")
            parameter = item[0].replace(' ', '_')
            if parameter == 'Этаж':
                values = re.findall('[0-9]+', item[1])
                characteristics['Этаж'] = values[0]
                if len(values) > 1:
                    characteristics['Этажей_в_доме'] = values[1]
            else:
                value = ''.join(re.findall(
                    r'(?u)\b[А-Яа-я0-9., ]+\b', item[1]))
                characteristics[parameter] = value

        # о доме
        house = soup.find_all(class_=re.compile('style-item-params-list-item'))
        for item in house:
            item = item.get_text()
            item = re.sub(r'[^A-Za-zА-Яа-яёЁ0-9.,: ]', '', item)
            item = item.split(":")
            parameter = item[0].replace(' ', '_')
            value = item[1]
            parameter = parameter.replace(',', '')
            characteristics[parameter] = value

        # ближайшие станции метро
        metro = soup.find_all(class_=re.compile(
            'style-item-address-georeferences-item-TZsrp'))
        for i in range(len(metro)):
            item = metro[i].get_text()
            item = item.replace('от ', '').replace(' мин.', '')
            item = item.replace('до ', '')
            digits = list(map(int, re.findall('[0-9]+', item)))

            station = re.sub(r'[^А-Яа-яёЁ -]', '', item)
            characteristics[f'Метро_{i+1}'] = station
            if digits:
                characteristics[f'Расстояние_до_метро_{i+1}'] = max(digits)

        # координаты
        coords = soup.find(class_=re.compile('style-item-map-wrapper'))
        characteristics['Широта'] = coords['data-map-lat']
        characteristics['Долгота'] = coords['data-map-lon']

        # добавляем информацию об объявлении в базу данных
        insert_into_database(characteristics)
    except:
        print(f"{link} error")
        return


def main():
    url = 'https://www.avito.ru/moskva/kvartiry/prodam/vtorichka-ASgBAQICAUSSA8YQAUDmBxSMUg?cd=1'
    get_advertisements(url)
    print('final')


if __name__ == "__main__":
    main()
