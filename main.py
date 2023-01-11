import requests
import schedule
from bs4 import BeautifulSoup
from datetime import datetime

url = 'https://www.marwin.kz/dir/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.3.818 Yowser/2.5 Safari/537.36"
}


def get_data():
    req = requests.get(url=url, headers=headers)
    req.encoding = 'UTF8'
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    # Сбор всех ссылок на каталоги
    catalogs_dict = []
    div_dir_item = soup.find('div', class_='all-products').find_all('div', class_='dir-item')
    for cat in div_dir_item:
        catalog = cat.find('ul', class_='list-level-2').find_all('li')
        for url_cat in catalog:
            catalogs_dict.append(url_cat.find('a').get('href'))

    # print(catalogs_dict)
    print(f'Количество каталогов: {len(catalogs_dict)}')

    try:
        # Сбор всех карточек товарами из каждого каталога
        url_products = []
        count_catalog = 0
        for url1 in catalogs_dict:
            count_catalog += 1
            page = 1
            max_count_cards_in_page = 0
            while True:
                req1 = requests.get(url=f'{url1}?p={page}', headers=headers)
                req1.encoding = 'UTF8'
                src1 = req1.text
                soup1 = BeautifulSoup(src1, 'lxml')

                if len(soup1.find_all('div', class_='message info empty')) != 0:
                    break

                cards_page = soup1.find('ol', class_='products list items product-items').find_all('li', class_='item product product-item')
                count_cards_in_page = 0
                for card in cards_page:
                    count_cards_in_page += 1
                    if len(card.find_all('span', class_='product-item__stock-label out-of-stock')) != 0:
                        continue
                    url_products.append(card.find('a', class_='product-item-link').get('href'))
                # print(url_products)

                if max_count_cards_in_page == count_cards_in_page:
                    if len(soup1.find_all('div', class_='pages')) == 0:
                        break
                    if len(soup1.find('div', class_='pages').find('ul', class_='items pages-items').find_all('li',class_='item pages-item-next disabled')) == 1:
                        break
                    print(f'Страница {page}')
                    page += 1

                elif max_count_cards_in_page < count_cards_in_page:
                    max_count_cards_in_page = count_cards_in_page
                    print(f'Страница {page}')
                    page += 1

                else:
                    print(f'Страница {page}')
                    break

            # print(len(url_products))
            # print(len(list(set(url_products))))
            print(f'{count_catalog} каталог готов!')

        print(len(url_products))
        print(len(list(set(url_products))))

    except Exception as ex:
        print(ex)
        print(url1)
        print(page)
        print(count_cards_in_page)

    list_products = [['Название', 'Цена', 'Бренд', 'Количество отзывов', 'Артикул', 'Каталог1', ' Каталог2', 'Ссылка']]
    count_parser = 0
    url_products = list(set(url_products))
    for url2 in url_products:
        try:
            req2 = requests.get(url=url2, headers=headers)
            req2.encoding = 'UTF8'
            src2 = req2.text
            soup2 = BeautifulSoup(src2, 'lxml')

            paths = soup2.find('div', class_='breadcrumbs').find_all('li')
            categories1 = f'{paths[1].text.strip()}'
            if len(paths) >= 3:
                categories2 = f'{paths[-2].text.strip()}'
            else:
                categories2 = 'Нет'

            if len(paths) == 5:
                name = paths[4].text.strip()
            else:
                name = paths[3].text.strip()

            if len(soup2.find_all('div', class_='esputnik-special-price')) == 1:
                price = soup2.find('div', class_='esputnik-special-price').text.strip()
            elif len(soup2.find_all('span', class_='price-container price-final_price tax weee')) == 1:
                price = soup2.find('span', class_='price-container price-final_price tax weee').text.strip()

            if len(soup2.find_all('table', class_='data table additional-attributes')) != 0:
                if soup2.find('table', class_='data table additional-attributes').find_all('tr')[0].find('th').text == 'Артикул':
                    article = soup2.find('table', class_='data table additional-attributes').find_all('tr')[0].find('td').text.strip()
                else:
                    article = 'Нет'

                if len(soup2.find('table', class_='data table additional-attributes').find_all('tr')) >= 2:
                    if soup2.find('table', class_='data table additional-attributes').find_all('tr')[1].find('th').text == 'Бренд':
                        brand = soup2.find('table', class_='data table additional-attributes').find_all('tr')[1].find('td').text.strip()
                    elif soup2.find('table', class_='data table additional-attributes').find_all('tr')[0].find('th').text == 'Бренд':
                        brand = soup2.find('table', class_='data table additional-attributes').find_all('tr')[0].find('td').text.strip()
                    else:
                        brand = 'Нет'
                else:
                    brand = 'Нет'

            if len(soup2.find_all('div', class_='tab-header')) != 0:
                if len(soup2.find('div', class_='tab-header').find_all('span', class_='counter')) != 0:
                    count_review = soup2.find('div', class_='tab-header').find('span', class_='counter').text.strip()
            else:
                count_review = 'Нет'

            list_products.append(
                [
                     name, price, brand, count_review, article, categories1, categories2, url2
                ]
            )
            # print(f'{categories1} - {categories2} - {name} - {price} - {article} - {brand} - {count_review} - {url2}')
            count_parser += 1
            print(f'{count_parser}/{len(list(set(url_products)))}')

        except Exception as ex:
            print(ex)
            print(f'Ошибка при ссылке {url2}')
            count_parser += 1
            print(f'Номер неспарсенного товара: {count_parser}')
            continue

    google_table(dict_cards=list_products)


def google_table(dict_cards):
    import os.path
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # mail bot 'parsers@parsers-372008.iam.gserviceaccount.com'
    SAMPLE_SPREADSHEET_ID = '107SdHe8_dV6npe_dKE-7xA2QJgxz6ZOywOy-GZyrZX0'
    SAMPLE_RANGE_NAME = 'marwin.kz!A1:H'

    try:
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        # Чистим(удаляет) весь лист
        array_clear = {}
        clear_table = service.clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,
                                    body=array_clear).execute()

        # добавляет информации
        array = {'values': dict_cards}
        response = service.append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range=SAMPLE_RANGE_NAME,
                                  valueInputOption='USER_ENTERED',
                                  insertDataOption='OVERWRITE',
                                  body=array).execute()

    except HttpError as err:
        print(err)


def main():
    start_time = datetime.now()

    schedule.every(1).second.do(get_data)
    while True:
        schedule.run_pending()

    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)


if __name__ == '__main__':
    main()
