import sqlite3


def main():
    connection = sqlite3.connect('houseprices.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE houseprices (
            ID INTEGER,
            Ссылка TEXT,
            Цена INTEGER,
            Дата TEXT,
            Адрес TEXT,
            Этаж REAL,
            Количество_комнат TEXT,
            Балкон_или_лоджия TEXT,
            Тип_комнат TEXT,
            Общая_площадь REAL,
            Жилая_площадь REAL,
            Площадь_кухни REAL,
            Высота_потолков TEXT,
            Санузел TEXT,
            Окна TEXT,
            Ремонт TEXT,
            Мебель TEXT,
            Тёплый_пол TEXT,
            Отделка TEXT,
            Техника TEXT,
            Способ_продажи TEXT,
            Вид_сделки TEXT,
            Тип_дома TEXT,
            В_доме TEXT,
            Год_постройки REAL,
            Этажей_в_доме REAL,
            Пассажирский_лифт TEXT,
            Грузовой_лифт TEXT,
            Парковка TEXT,
            Двор TEXT,
            Название_новостройки TEXT,
            Корпус_строение TEXT,
            Официальный_застройщик TEXT,
            Тип_участия TEXT,
            Срок_сдачи TEXT,
            Метро_1 TEXT,
            Метро_2 TEXT,
            Метро_3 TEXT,
            Расстояние_до_метро_1 REAL,
            Расстояние_до_метро_2 REAL,
            Расстояние_до_метро_3 REAL,
            Широта REAL,
            Долгота REAL,
            Запланирован_снос TEXT
            )
            """
                   )
    connection.close()
    print("Successful")


if __name__ == "__main__":
    main()
