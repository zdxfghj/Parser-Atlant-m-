import xlsxwriter
from bs4 import BeautifulSoup
import requests
import json

url = 'https://cheryauto.by/available-cars/'




PAGES_COUNT = 11
OUT_JSON_FILENAME = 'out.json'
OUT_XLSX_FILENAME = 'out.xlsx'
OUT_XML_FILENAME = 'out.xml'

def crawl_products(pages_count):
    urls = []
    fmt = 'https://cheryauto.by/available-cars/?utm_source=google&utm_medium=cpc&utm_campaign=chery_brand_google_search_rb&utm_term=%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%BE%D0%B1%D0%B8%D0%BB%D1%8C+%D0%BA%D0%B8%D1%82%D0%B0%D0%B9%D1%81%D0%BA%D0%B8%D0%B9&utm_content=&gad_source=1&gclid=CjwKCAjwg8qzBhAoEiwAWagLrIXVW2RZ17qHOCjuj0-ECXKgniuD4ra8AoZzrBLfCIvGWK9i3MLcaBoCU4EQAvD_BwE&PAGEN_1={page}'

    for page_n in range(1, 1 + pages_count):
        print('page: {}'.format(page_n))
        page_url = fmt.format(page=page_n)
        soup = get_soup(page_url)
        if soup is None:
            break

        for tag in soup.select('.card-stock .link-block'):
            href = tag.attrs['href']
            url = 'https://cheryauto.by{}'.format(href)
            urls.append(url)

    return urls


def parse_products(urls):
    data = []

    for url in urls:
        print('product: {}'.format(url))

        soup = get_soup(url)
        if soup is None:
            break

        folder_id = soup.select_one('.car-header__titles h1').text.strip()
        [modification_id,year] = soup.select_one('.car-header__kit').text.strip().split(',')
        year = year.strip()
        images = soup.select_one('.car-body__image img').attrs['src']
        body_type = 'Седан' if folder_id == 'Arrizo 8' else 'Кроссовер'
        vin = soup.select_one('.car-body__list .car-body__item:nth-of-type(6)  p b').text.strip()
        custom = soup.select_one('.car-body__list .car-body__item:nth-of-type(4)  p b').text.strip()
        color = soup.select_one('.car-body__list .car-body__item:nth-of-type(5)  p b').text.strip()
        availability = soup.select_one('.status-block__text').text.strip()
        if soup.select_one('.car-price .car-price__actual') is None:
            price = ""
            currency=''
        else:
            [price,currency] = soup.select_one('.car-price .car-price__actual').text.rsplit(' ', maxsplit=1)
        item = {
            'mark_id': 'Chery',
            'folder_id': folder_id,
            'modification_id': modification_id,
            'url': url,
            'images': images,
            'body_type':body_type,
            'color':color,
            'availability': availability,
            'custom': custom,
            'year': year,
            'price':price,
            'currency':currency,
            'vin':vin,
            'owners_number': 'Не было владельцев',



        }
        data.append(item)

    return data


def get_soup(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup

def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    with open(OUT_JSON_FILENAME, 'w') as f:
        json.dump(data, f, **kwargs)


def dump_to_xlsx(filename, data):
    if not len(data):
        return None

    with xlsxwriter.Workbook(filename) as workbook:
        ws = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        headers = []
        headers.extend(data[0].keys())

        for col,h in enumerate(headers):
            ws.write_string(0, col, h, cell_format=bold)

        for row, item in enumerate(data, start=1):
            ws.write_string(row, 0, item['mark_id'])
            ws.write_string(row, 1, item['folder_id'])
            ws.write_string(row, 2, item['modification_id'])
            ws.write_string(row, 3, item['url'])
            ws.write_string(row, 4, item['images'])
            ws.write_string(row, 5, item['body_type'])
            ws.write_string(row, 6, item['color'])
            ws.write_string(row, 7, item['availability'])
            ws.write_string(row, 8, item['custom'])
            ws.write_string(row, 9, item['year'])
            ws.write_string(row, 10, item['price'])
            ws.write_string(row, 11, item['currency'])
            ws.write_string(row, 12, item['vin'])
            ws.write_string(row, 13, item['owners_number'])

def dump_to_xml(filename, data):
    f = open(filename, "w",encoding='utf-8')
    f.write("<?xml version='1.0'?>\n<root>\n")
    f.write("\t<data>\n\t\t<cars>\n")

    for obj in data:
        f.write("\t\t\t<car>\n")
        for item_name, item_value in obj.items():
            f.write(f'\t\t\t\t<{item_name}>{item_value}</{item_name}>\n')
        f.write("\t\t\t</car>\n")


    f.write("\n\t\t</cars>\n\t</data>\n</root>")
    f.close()

def main():
    print(f"Введите количество обновлений списков авто:")
    pages_count = int(input())
    urls = crawl_products(pages_count) # You can use global  PAGES_COUNT = 11
    data = parse_products(urls)
    dump_to_xlsx(OUT_XLSX_FILENAME, data)
    dump_to_json(OUT_JSON_FILENAME, data)
    dump_to_xml(OUT_XML_FILENAME, data)

if __name__ == '__main__':
    main()
