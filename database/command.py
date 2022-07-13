from . import history
from config_data.config import HISTORY


def save_request_to_db(hotels: list, user_id, sort, city, city_id, check_in, check_out, **kwarg) -> None:
    """
    Функция сохраняет запрос пользователя и полученный список отелей в базу данных.
    :return: None
    """

    with history:
        row = history.execute("""
        INSERT INTO request (user, city, checkin, checkout, sort)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, city_id, check_in, check_out, sort))

        req_id = row.lastrowid

        for hotel in hotels:
            history.execute("""
            INSERT INTO history
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (req_id, *hotel.values()))

        history.execute("""
        REPLACE INTO city
        VALUES (?, ?)
        """, (city_id, city))


def get_history_from_db(user_id: int) -> list:
    """
    Возвращает последние запросы пользователя из базы.
    Количество запросов - параметр HISTORY в файле конфигурации.
    :param user_id: ID пользователя.
    :return: Список кортежей с данными запросов
    """
    with history:
        cur = history.execute("SELECT req_id, date, (SELECT name FROM city WHERE id=request.city) AS city, "
                              "checkin, checkout, sort FROM request WHERE user=:user", {'user': user_id})
    return cur.fetchall()[-HISTORY:]


def get_last(user_id: int) -> list:
    """
    Возвращает из базы последний запрос пользователя
    :param user_id: ID пользователя
    :return: Кортеж с данными запроса
    """
    with history:
        return history.execute("SELECT date, city AS city_id, (SELECT name FROM city WHERE id=request.city) AS city, "
                               "checkin, checkout, sort FROM request WHERE user=(?) ORDER BY date DESC LIMIT 1",
                               (user_id,)).fetchall()


def get_req_from_db(req_id: str) -> tuple:
    """
    Возвращает запрос.
    :param req_id: ID запроса
    :return: кортеж с данными запроса
    """
    with history:
        cur = history.execute("SELECT date, city AS city_id, (SELECT name FROM city WHERE id=request.city) AS city, "
                              "checkin, checkout, sort FROM request WHERE req_id=:req", {'req': req_id})
    return cur.fetchall()[0]


def get_hotel_by_req(req_id: str) -> list:
    """
    Возвращает из базы отели, соответствующие запросу.
    :param req_id: ID запроса
    :return: Список словарей с данными найденных отелей
    """
    with history:
        records = history.execute("SELECT * FROM history WHERE req_id=(?)", (req_id,)).fetchall()
    hotels = []
    for record in records:
        hotels.append({
            'id': record[1],
            'url': record[2],
            'name': record[3],
            'address': record[4],
            'price': record[5],
            'latitude': record[6],
            'longitude': record[7],
        })
    return hotels
