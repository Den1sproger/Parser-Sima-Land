# Script for getting data from the Sima Land store
# Getting characteristics about each product, downloading images for each in high resolution
# The characteristics are recorded in a csv file
# The images are saved in separated directory
# Each image had a unique name
# Скрипт получения данных из магазина Sima Land
# Получение характеристик по каждому товару, загрузка изображений каждого товара в максимально высоком разрешении
# Запись характеристик в csv файл
# Изображения сохраняются в отдельную папку
# Каждое изображение имеет уникальное название

# Links for scrapping:
# Ссылки для парсинга:
# 'https://www.sima-land.ru/girlyandy/?c_id=31129',
# 'https://www.sima-land.ru/prazdniki/novyy-god/girlyandy-i-prazdnichnoe-osveschenie/svetodiodnye-figury/?c_id=1031',
# 'https://www.sima-land.ru/svetodiodnye-pribory/?c_id=1010',
# 'https://www.sima-land.ru/svetodiodnye-derevya/?c_id=40307',
# 'https://www.sima-land.ru/neonovye-shnury-i-komplektuyushchie/?c_id=40305',
# 'https://www.sima-land.ru/svetodiodnye-lenty-i-komplektuyushchie/?c_id=40299'


import time
import os
import csv

import requests
import lxml

from bs4 import BeautifulSoup
from myheaders import headers, path


list_json = [
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=10&category_id=31129&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=1686293227' for i in range(1, 44)],
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=10&category_id=1031&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=27503892' for i in range(1, 73)],
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=10&category_id=1010&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=1686293227' for i in range(1, 9)],
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=20&category_id=40307&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=1686293227' for i in range(1, 4)],
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=20&category_id=40305&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=1686293227' for i in range(1, 3)],
    [f'https://www.sima-land.ru/iapi/product-list/items/v1/default-view/?page={i}&sort=price&currency=RUB&per-page=10&category_id=40299&page_type=category&f=null&with_adult=1&modifier_limit=5&settlement_id=1686293227' for i in range(1, 3)]
]

def create_csv(filename: str) -> None:
    # creating a csv file
    # создание csv файла
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                'IE_XML_ID',
                'IE_NAME',
                'IE_PREVIEW_PICTURE',
                'IE_PREVIEW_TEXT',
                'IE_PREVIEW_TEXT_TYPE',
                'IE_DETAIL_PICTURE',
                'IE_DETAIL_TEXT',
                'IE_DETAIL_TEXT_TYPE',
                'IE_CODE',
                '',
                'IP_PROP526',
                'IP_PROP532',
                'IP_PROP554',
                'IC_GROUP0',
                'IC_GROUP1',
                'IC_GROUP3',
                ''
            )
        )

def add_info_to_csv(filename: str, string: list) -> None:
    # adding another product to file
    # добавление информации по очередному товару в csv файл
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(string)

def get_urls(session) -> list:
    # getting links to all products
    # получение списка ссылок на все товары
    list_urls = []
    for items in list_json:
        try:
            for url in items:
                req = session.get(url=url, headers=headers)
                information = req.json()
                for item in information['items']:
                    href = 'https://www.sima-land.ru' + item.get('url')
                    list_urls.append(href)
        except Exception as ex:
            print(ex)
        finally:
            time.sleep(0.2)
    return list_urls

def get_price_1(text: str) -> str:
    # getting a price without spaces
    # получение цены без пробелов
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    new = text
    for i in text:
        if i not in numbers:
            new = new.replace(i, '')
    return new

def get_price_2(text: str) -> str:
    # getting a price with spaces
    # получение цены с пробелами
    new = get_price_1(text=text)
    if len(new) > 3:
        new = new[::-1]
        count = 0
        whitespace = 0
        for i in new:
            count += 1
            if count % 3 == 0:
                new = new[:count + whitespace] + ' ' + new[count + whitespace:]
                whitespace += 1
        new = new[::-1]
    return new + ' #CURRENCY#'

def download_img(images: list, number: int, session) -> None:
    # downloading images from one product
    # загрузка фотографий одного товара
    count = 0
    for image in images:
        count += 1
        url = image.replace('140.jpg', '1600.jpg')
        response = session.get(url=url)
        with open(fr'data\images\image_{number}_{count}.png', 'wb') as file:
            file.write(response.content)

def get_data():
    # getting product data
    # получение данных о товарах
    session = requests.Session()
    list_urls_products = get_urls(session)

    total_products = len(list_urls_products)
    count = 0
    number_in_base = 549
    for url_product in list_urls_products:
        count += 1
        number_in_base += 1
        try:
            response = session.get(url=url_product, headers=headers)

            with open(f'data_html\product_{count}.html', 'w', encoding='utf-8') as file:
                file.write(response.text)

            with open(f'data_html\product_{count}.html', 'r', encoding='utf-8') as file:
                src = file.read()

            soup = BeautifulSoup(src, 'lxml')
            product_name = soup.find('h1', class_='fArxp').text
            preview_picture = soup.find('div', class_='l4Oe9').\
                find('img').get('src')
            preview_text = soup.find('div', class_='FUSJU')
            if preview_text:
                preview_text = preview_text.find('p')
            else:
                preview_text = ''
            detail_picture = preview_picture
            detail_text = preview_text
            id_code = url_product.removeprefix('https://www.sima-land.ru/')[8:-1]
            number = url_product.removeprefix('https://www.sima-land.ru/')[0:6]
            price_1 = get_price_1(
                soup.find('div', class_='JJZjK').find('span', class_='LTJlA').text
            )
            price_2 = get_price_2(
                soup.find('div', class_='JJZjK').find('span', class_='LTJlA').text
            )
            if soup.find('div', class_='ltTSd'):
                additional_images = [
                    i.get('src') for i in soup.find('div', class_='ltTSd').find_all('img')[1:]
                ]
            else:
                additional_images = []
            first_section = soup.find('div', class_='YYIiA').find_all('div', class_='R1eGv')[1].text
            second_section = soup.find('div', class_='YYIiA').find_all('div', class_='R1eGv')[2].text
            third_section = soup.find('div', class_='YYIiA').find_all('div', class_='R1eGv')[3]
            if third_section:
                third_section = third_section.text
            else:
                third_section = ''

            data = [
                number_in_base,
                product_name,
                preview_picture,
                preview_text,
                'html',
                detail_picture,
                detail_text,
                'html',
                id_code,
                number,
                price_1,
                price_2,
                '',
                first_section,
                second_section,
                third_section,
            ]

            specifications = soup.find('div', class_='CwDGt').find_all('div', class_='w1wNn')
            for item in specifications:
                characteristics = item.find_all('div', class_='S3jLY')
                for characteristic in characteristics:
                    char_name = characteristic.find('div', class_='property-name').text
                    char = characteristic.find('div', class_='qAQCt').text
                    data.append('')
                    data.append(char_name)
                    data.append(char)

            if additional_images != []:
                for image in additional_images:
                    data[12] = image
                    add_info_to_csv(
                        filename=r'data\result.csv',
                        string=data
                    )
            else:
                add_info_to_csv(
                    filename=r'data\result.csv',
                    string=data
                )
            additional_images.append(preview_picture)
            download_img(
                images=additional_images,
                number=number_in_base,
                session=session
            )
        except Exception as ex:
            print(ex)
        else:
            print(f'[INFO] Iteration {count}/{total_products} is completed')
        finally:
            time.sleep(0.2)

def main():
    start_time = time.time()
    os.chdir(path)

    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data\images'):
        os.mkdir('data\images')
    create_csv(r'data\result.csv')
    get_data()
    finish_time = time.time() - start_time
    print(f'Worked time: {finish_time}')


if __name__ == '__main__':
    main()
