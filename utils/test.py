import os
import requests
import json
from collections import Counter
from typing import Union, Optional, Literal, List, Dict, Final
from config_data.config import RAPID_API_KEY
from PIL import Image

"""
Файл с функциями для теста API. В работе не используется
"""


def request_to_api_hotel(querystring: dict, mode: Literal['des', 'hotel', 'foto'] = 'hotel', to_file=False) -> Optional[dict]:
    """
    Базовя функция запроса к API Hotels
    :param mode: тип запрашиваемых данных:
                'des' - подходящие местоположения
                'hotel' - список отелей, значение по умолчанию
    :param querystring: строка запроса
    :param to_file: запись полученного ответа в файл
    :return: json извлеченный из ответа (dict), если за 3 попытки не удалось получить ответ, то None
    """
    endpoint = 'properties/list'
    if mode == 'des':
        endpoint = 'locations/v2/search'
    elif mode == 'foto':
        endpoint = 'properties/get-hotel-photos'

    url = 'https://hotels4.p.rapidapi.com/' + endpoint
    headers = {'X-RapidAPI-Host': 'hotels4.p.rapidapi.com', 'X-RapidAPI-Key': RAPID_API_KEY}
    for i in range(3):
        try:
            print(f'Запрос, попытка {i + 1} ::: {querystring}')
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
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


def write_response(resp: dict) -> None:
    """
    Функция записи результата запроса в файл
    :param resp: json объект полученный из запроса
    :return: None
    """
    while 'materials' not in os.listdir():
        os.chdir('..')
    file_name = 'materials\\api_request\\'
    try:
        file_name += 'HOTEL_' + resp['data']['body']['header']
    except KeyError:
        if resp.get('term'):
            file_name += 'DES_' + str(resp.get('term'))
        else:
            file_name += 'FOTO_' + str(resp.get('hotelId', 'no'))
    file_name += '.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(resp, file, indent=4, ensure_ascii=False)


def get_photo(id_hotel: int, file_name = ''):
    """
    Функция-генератор, получает от API  данные по фото
    :param id_hotel: ID отеля
    :return: ссылки на фото отелей
    """
    if file_name:
        with open('..\\materials\\api_request\\' + file_name, 'r') as file:
            response = json.load(file)
    else:
        querystring = {"id": id_hotel}
        response = request_to_api_hotel(querystring, 'foto', to_file=True)
    count = Counter()
    print('Всего фото:', len(response['hotelImages']))
    suffix = {i: set() for i in range(21)}
    for elem in response['hotelImages']:
        for types in elem['sizes']:
            suffix[types['type']].add(types['suffix'])

    suffix = {key: ''.join(values) for key, values in suffix.items()}
    print(json.dumps(dict(suffix), indent=4))


def all_photo():
    path = '..\\materials\\api_request\\'
    suffix = {i: set() for i in range(21)}
    for file in [f for f in os.listdir(path) if f.startswith('FOTO_')]:
        with open(path + file, 'r') as f:
            response = json.load(f)
        for elem in response['hotelImages']:
            for types in elem['sizes']:
                suffix[types['type']].add(types['suffix'])
        print(len([a for a in suffix.values() if a]), end=' ')

    suffix = {key: ''.join(values) for key, values in suffix.items()}
    print(json.dumps(dict(suffix), indent=4))


def resolution_photo():
    path = '..\\materials\\api_request\\'
    suffix = dict()
    for file in [f for f in os.listdir(path) if f.startswith('FOTO_')]:
        print(file)
        with open(path + file, 'r') as f:
            response = json.load(f)
        for elem in response['hotelImages'][::10]:
            base_url: str = elem['baseUrl']
            for types in elem['sizes']:
                url = base_url.replace('{size}', types['suffix'])
                try:
                    r = requests.get(url, stream=True).raw
                    img = Image.open(r)

                    key = (types['type'], types['suffix'])
                    if not suffix.get(key):
                        suffix[key] = set()
                    suffix[key].add(img.size)
                except requests.exceptions.RequestException as msg:
                    print('Ошибка', msg, url)

    for key, val in suffix.items():
        print(key, ':::', val)




# get_photo(309940, 'FOTO_309940.json')
# get_photo(1270431648)
# all_photo()

resolution_photo()