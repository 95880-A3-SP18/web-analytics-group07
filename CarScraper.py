import os, sys, requests, bs4, requests.exceptions, OpenSSL.SSL, ssl, urllib3.exceptions, requests.exceptions


def open_car_links():

    search_result_pages = []
    search_result_pages.append('https://www.truecar.com/used-cars-for-sale/listings/location-pittsburgh-pa/')

    for page in range(370):
        search_result_pages.append('https://www.truecar.com/used-cars-for-sale/listings/' +
                                   'location-pittsburgh-pa/?page=' + str(page + 2))

    car_links = []

    for i, page_link in enumerate(search_result_pages):
        try:
            print("processing page" + str(i))
            response = requests.get(page_link)
            response.raise_for_status()
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            links = soup.select('div[data-qa="SearchResults"] div[data-qa="VehicleCardPricing"] p[class="cta"] a')
            for link in links:
                car_links.append('https://www.truecar.com' + link.get('href'))
        except requests.exceptions.HTTPError:
            print("can't open page link: " + page_link)

    download_car_data(car_links)


def download_car_data(car_links):
    brand_list = []
    model_list = []
    year_list = []
    car_name_list = []
    price_list = []
    trim_list = []
    exterior_color_list = []
    interior_color_list = []
    mileage_list = []
    mpg_list = []
    transmission_list = []
    engine_list = []
    drive_type_list = []
    fuel_type_list = []
    included_features_list = []
    car_data = [car_name_list, price_list, brand_list, model_list, year_list, trim_list, exterior_color_list,
                interior_color_list, mileage_list, mpg_list, transmission_list, engine_list,
                drive_type_list, fuel_type_list, included_features_list]

    car_dict = {1: 'car_name',
                2: 'price',
                3: 'brand',
                4: 'model',
                5: 'year',
                6: 'trim',
                7: 'exterior_color',
                8: 'interior_color',
                9: 'mileage',
                10: 'mpg',
                11: 'transmission',
                12: 'engine',
                13: 'drive_type',
                14: 'fuel_type',
                15: 'included_features'}

    for i, link in enumerate(car_links):
        try:
            print("processing link" + str(i))
            res = requests.get(link)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, 'html.parser')

            car_name = soup.select('h1 .text-truncate')[0].text
            car_name_list.append(car_name)

            price = soup.select('div[data-qa="LabelBlock-text"] span')[0].text
            price = price.replace(',', '')
            price_list.append(price)

            navigation_info = soup.select('ol[class="hidden-md-down _2xw6veo breadcrumb"] li a')
            brand_list.append(navigation_info[3].text)
            model_list.append(navigation_info[4].text)
            year_list.append(navigation_info[5].text)

            features = soup.select('div[data-qa="EmphasizedFeatures"] span[class="emphasized-feature-description"]')
            trim_list.append(features[0].text)
            exterior_color_list.append(features[1].text)
            interior_color_list.append(features[2].text)
            mileage_list.append(features[3].text.replace(',', ''))
            mpg_list.append(features[4].text)
            transmission_list.append(features[5].text)
            engine_list.append(features[6].text)
            drive_type_list.append(features[7].text)
            fuel_type_list.append(features[8].text)

            included_features = soup.select('div[data-qa="ReadMore"] div[class="read-more-body spacing-2"] p')
            try:
                included_features_list.append(included_features[0].text)
            except IndexError:
                print("no included_features")
                included_features_list.append('')

        except requests.exceptions.HTTPError or OpenSSL.SSL.SysCallError or ssl.SSLError or urllib3.exceptions.MaxRetryError or requests.exceptions.SSLError:
            print("can't open car link: " + link + str(i))

    # write into csv file
    data = []
    label = ""
    for col, feature in enumerate(car_data):
        label += car_dict[col + 1] + ','
    data.append(label)

    for row, car in enumerate(car_name_list):
        record = ""
        for col, feature in enumerate(car_data):
            record += car_data[col][row] + ','
        data.append(record)

    csv_file = open('car_data.csv', 'w')
    for row in data:
        csv_file.write(row + '\n')


if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    open_car_links()
