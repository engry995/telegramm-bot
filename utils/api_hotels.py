import os
import requests
import json
import re
import random
from typing import Union, Optional, Literal, List, Dict, Final, Generator
from config_data.config import RAPID_API_KEY, DES_TO_FILE, HOTELS_TO_FILE, FOTO_TO_FILE, RESPONSE_FROM_FILE


def request_to_api_hotel(querystring: dict, mode: Literal['des', 'hotel', 'foto'] = 'hotel',
                         to_file: bool = False) -> Optional[dict]:
    """
    Базовая функция запроса к API Hotels
    :param mode: тип запрашиваемых данных:
                'des' - подходящие местоположения
                'hotel' - список отелей, значение по умолчанию
    :param querystring: строка запроса
    :param to_file: запись полученного ответа в файл
    :return: json извлеченный из ответа (dict), если за 3 попытки не удалось получить ответ, то None
    """
    if RESPONSE_FROM_FILE and mode != 'hotel':
        file_name = ''
        if mode == 'des':
            file_name = 'DES_' + querystring['query']
        elif mode == 'foto':
            file_name = f'FOTO_{querystring["id"]}'
        file_name = r'materials\\api_request\\' + file_name + '.json'
        print('Попытка выполнить запрос из файла. Ищем файл:', file_name, end=' ')
        if os.path.isfile(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                response = json.load(file)
            print(' -->>> Файл найден. Запрос выполнен из файла')
            return response
        else:
            print(' -->>> Файл не найден. Запрос выполняется из API')

    endpoint = 'properties/list'
    if mode == 'des':
        endpoint = 'locations/v2/search'
    elif mode == 'foto':
        endpoint = 'properties/get-hotel-photos'

    url = 'https://hotels4.p.rapidapi.com/' + endpoint
    headers = {'X-RapidAPI-Host': 'hotels4.p.rapidapi.com', 'X-RapidAPI-Key': RAPID_API_KEY}
    for i in range(3):
        try:
            print(f'Запрос, попытка {i + 1} ::: {querystring} -->>> ', end='')
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            if response.status_code == 200:
                print('Ответ успешно получен.')
                break
        except requests.exceptions.RequestException as message:
            print('Ошибка request', message)
    else:
        return None

    response.encoding = 'utf-8'
    response = response.json()
    if to_file:
        write_response(response)
    return response


def get_destination(location: str) -> Optional[Dict[str, str]]:
    """
    Функция получения от API Hotels местоположений, подходящих по названию.
    :param location: строка для поиска
    :return: словарь(ключ - наименование локации: значение - id локации)
    """
    querystring = {"query": location, "locale": "ru_RU", "currency": "USD"}
    response = request_to_api_hotel(querystring, 'des', DES_TO_FILE)
    if not response:
        return None
    result = {}
    for elem in response['suggestions']:
        if elem['group'] in ['CITY_GROUP', 'TRANSPORT_GROUP']:
            for line in elem['entities']:
                name = re.sub(r'<.*?>', '', line['caption'])
                result[name] = line['destinationId']
    return result


def get_hotels(data: dict, **params) -> List[dict]:
    """
    Получает текущее состояние пользователя, формируется базовая строка запроса для получения списка отелей,
    объединяется с params, запрашиваются отели. Формируется список с данными по отелям. Данные запрашиваются
    при необходимости несколько раз, чтобы получить нужное количество отелей.
    :param data: текущие данные пользователя.
    :param params: данные для объединения со строкой запроса для необходимой сортировки или фильтрации
                    по умолчанию сортировка по возрастанию цены.
    :return: список, элемент списка - словарь с данными об отеле
    """

    def get_address(address: dict) -> str:
        if not address:
            return 'Не определен'
        res = ', '.join([address.get('locality', ''),
                         address.get('streetAddress', ''),
                         address.get('extendedAddress', '')])
        return res

    def get_price(price: dict):
        try:
            cost = price['price']['exactCurrent']
        except (TypeError, KeyError):
            return 'Стоимость: нет данных.'
        return f'За сутки {cost}$. Всего {cost * stay_day:.2f}$ за {stay_day} {end}'

    def parse(hotel: dict) -> dict:
        item = {
            'id': hotel['id'],
            'url': f'https://www.hotels.com/ho{hotel["id"]}',
            'name': f"{'★' * int(hotel.get('starRating', 0))} {hotel.get('name', '-')}",
            'address': get_address(hotel.get('address')),
            'price': get_price(hotel.get('ratePlan')),
            'latitude': hotel['coordinate']['lat'],
            'longitude': hotel['coordinate']['lon'],
        }
        return item

    #  переменные stay_day и end используются во вложенной функции get_price
    stay_day: Final[int] = (data['check_out'] - data['check_in']).days
    if stay_day == 1:
        end = 'ночь'
    elif stay_day < 5:
        end = 'ночи'
    else:
        end = 'ночей'

    form = '%Y-%m-%d'
    querystring = {
        "destinationId": data['city_id'],
        "pageNumber": 1,
        "pageSize": "25",
        "checkIn": data['check_in'].strftime(form),
        "checkOut": data['check_out'].strftime(form),
        "adults1": "2",
        "sortOrder": "PRICE",  # по умолчанию, сортировка по возрастанию цены
        "locale": "ru_RU",
        "currency": "USD",
    }
    querystring.update(params)
    result = []
    page_number = 1
    while len(result) < data['number_hotels']:
        response = request_to_api_hotel(querystring, to_file=HOTELS_TO_FILE)
        if not response:
            break
        response = response['data']['body']['searchResults']['results']  # оставляем список отелей
        print(response)
        result.extend([parse(hotel) for hotel in response])
        page_number += 1
        querystring.update({"pageNumber": page_number})

    return result[:data['number_hotels']]


def get_photo(id_hotel: int) -> Generator:
    """
    Функция-генератор, получает от API  данные по фото
    :param id_hotel: ID отеля
    :return: ссылки на фото отелей
    """
    querystring = {"id": id_hotel}
    response = request_to_api_hotel(querystring, 'foto', to_file=FOTO_TO_FILE)
    response = response['hotelImages']
    while True:  # если мало фото, генератор не остановится
        random.shuffle(response)
        for elem in response:
            # Возьмем суффикс 'y' как подходящие по разрешению фото, см. materials\resolution.txt
            url = elem['baseUrl'].replace('{size}', 'y')
            yield url


def write_response(resp: dict) -> None:
    """
    Функция записи результата запроса в файл
    :param resp: json объект полученный из запроса
    :return: None
    """
    while 'materials' not in os.listdir():
        os.chdir('..')
    file_name = os.path.join('materials', 'api_request')
    try:
        file_name = os.path.join(file_name, 'HOTEL_' + resp['data']['body']['header'])
    except KeyError:
        if resp.get('term'):
            file_name = os.path.join(file_name, 'DES_' + str(resp.get('term')))
        else:
            file_name = os.path.join(file_name, 'FOTO_' + str(resp.get('hotelId', 'no')))
    file_name += '.json'
    print(file_name)
    print(os.path.abspath(file_name))
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(resp, file, indent=4, ensure_ascii=False)


def reverse_geocode(latitude: Union[str, float], longitude: Union[str, float]) -> Optional[str]:
    """
    Определение адреса (города) по координатам.
    :param latitude: широта
    :param longitude: долгота
    :return: наименование города по этим координатам. None - если не удалось определить город.
    """

    url = "https://forward-reverse-geocoding.p.rapidapi.com/v1/reverse/"
    querystring = {"lat": str(latitude), "lon": str(longitude), "accept-language": "en", "polygon_threshold": "0.0"}
    headers = {"X-RapidAPI-Host": "forward-reverse-geocoding.p.rapidapi.com", "X-RapidAPI-Key": RAPID_API_KEY}

    city = None
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except requests.exceptions:
        return None

    if response.status_code == 200:
        response = response.json()
        if response.get('error') is None:
            city = response.get('address').get('city')

    return city
