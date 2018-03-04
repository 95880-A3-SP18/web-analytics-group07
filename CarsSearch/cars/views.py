import collections
from django.shortcuts import render


from django.http import HttpResponseRedirect


import os, sys, requests, bs4


def index(request):
    return render(request, 'cars/index.html')


def results(request):
    if request.method == 'POST':
        mileage = request.POST["mileage"]
        brand = request.POST["brand"]
        transmission = request.POST["transmission"]
        mpg = request.POST["mpg"]
        year = request.POST["year"]
        url = redirect(mileage,brand,year)
        price = regression(mileage, brand, year, transmission, mpg)
        price = "${:,}".format(price)
        print(price)
        print(url)
    return render(request, 'cars/results.html',{'url': url, 'price': price})

#scrape www.truecar.com to get great recommendation
def redirect(mileage,brand,year):
    l = brand.split()
    brand = l[0].lower()
    model =l[1].lower()
    if len(l) > 2:
        model=l[1]+' '+l[2]
        model=model.lower()
    url = "https://www.truecar.com/used-cars-for-sale/listings/{0}/{1}/year-{2}-max/location-pittsburgh-pa/?mileageHigh={3}".format(brand,model,year,mileage)
    return url


# use the model we build to predict market price of the car and visualize data
def regression(mileage_input,brand_input,year_input,transmission_input,mpg_input):
    l = brand_input.split()
    brand_input = l[0]
    model_input = l[1]
    if len(l) > 2:
        model_input = l[1] + ' ' + l[2]
    import csv, pandas as pd, numpy as np, statsmodels.formula.api as smf, collections
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # read data from csv file
    price = []
    brand = []
    models = []
    year = []
    trim = []
    mileage = []
    mpg = []
    transmission = []
    engine = []
    drive_type = []
    fuel_type = []

    with open('cars/static/cars/car_data_cleaned.csv', encoding='ISO-8859-1') as data:
        data_reader = csv.reader(data, delimiter=',')
        next(data_reader)
        for row in data_reader:
            price.append(int(row[1].strip().replace('$', '').replace(',', '')))
            brand.append(row[2].strip())
            models.append(row[3].strip())
            year.append(int(row[4].strip()))
            trim.append(row[5].strip())
            mileage.append(int(row[8].strip()))
            mpg.append(row[9].strip())
            transmission.append(row[10].strip())
            engine.append(row[11].strip())
            drive_type.append(row[12].strip())
            fuel_type.append(row[13].strip())
        # dataset used to do regression
    df = pd.DataFrame({
        'price': price,
        'brand': brand,
        'mileage': mileage,
        'year': year,
        'transmission': transmission,
        'mpg': mpg,
        'model': models
    })
    # regression
    res = smf.ols(formula='price ~ mileage + C(brand) + year + C(transmission) + mpg + C(model)', data=df).fit()
    newdata = pd.DataFrame({
        'brand': [brand_input],
        'mileage': [int(mileage_input)],
        'year': [int(year_input)],
        'transmission': [transmission_input],
        'mpg': [mpg_input],
        'model': [model_input]
    })
    result = res.predict(newdata)

    # Visualize the data, plot year
    df['brand'] = df[df['brand'] == brand_input]['brand']
    brand_data = df.dropna()

    counter = collections.Counter(brand_data['year'])
    year_count = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    year_count.columns = ['year', 'count']
    year_count = year_count.sort_values('year', ascending=False)
    total_count = len(brand_data['year'])
    indexes = np.arange(len(year_count['year']))
    width = 1
    plt.style.use('seaborn-pastel')
    fig, ax = plt.subplots(figsize=(10, 5))
    rects = ax.bar(indexes, year_count['count'], width, edgecolor="grey")
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 1,
                '%.1f%% (%d)' % (float(height) * 100 / total_count, int(height)), ha='center', va='center')
    ax.set_xlabel('Year', fontsize=15)
    plt.xticks(indexes, year_count['year'])
    plt.title('Number of ' + brand_input + ' on Sale by Year', fontsize=18)
    plt.tight_layout()
    plt.legend()
    plt.savefig('cars/static/cars/image/plot1.png')
    plt.close()

    # plot model
    df['brand'] = df[df['brand'] == brand_input]['brand']
    brand_data = df.dropna()
    counter = collections.Counter(brand_data['model'])
    model_count = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    model_count.columns = ['model', 'count']
    model_count = model_count.sort_values('model', ascending=False)
    total_count = len(brand_data['model'])
    indexes = np.arange(len(model_count['model']))
    width = 1
    plt.style.use('seaborn-pastel')
    fig, ax = plt.subplots(figsize=(10, 5))
    rects = ax.bar(indexes, model_count['count'], width, edgecolor="grey")
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 1,
                '%.1f%% (%d)' % (float(height) * 100 / total_count, int(height)), ha='center', va='center')
    ax.set_xlabel('Model', fontsize=15)
    plt.xticks(indexes, model_count['model'])
    plt.title('Number of ' + brand_input + ' on Sale by Model', fontsize=18)
    plt.legend()
    plt.tight_layout()
    plt.savefig('cars/static/cars/image/plot2.png')
    plt.close()

    # plot mpg
    df['brand'] = df[df['brand'] == brand_input]['brand']
    brand_data = df.dropna()
    counter = collections.Counter(brand_data['mpg'])
    total_count = len(brand_data['mpg'])
    model_count = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    model_count.columns = ['mpg', 'count']
    model_count = model_count.sort_values('mpg', ascending=False)
    indexes = np.arange(len(model_count['mpg']))
    width = 1
    plt.style.use('seaborn-pastel')
    fig, ax = plt.subplots(figsize=(10, 5))
    rects = ax.bar(indexes, model_count['count'], width, edgecolor="grey")
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 0.5,
                '%.1f%%' % (float(height) * 100 / total_count), ha='center', va='center')
    plt.xticks(indexes, model_count['mpg'],rotation=30, horizontalalignment='right')
    plt.title('Number of ' + brand_input + ' on Sale by Miles per Gallon', fontsize=18)
    ax.set_xlabel('Mile per Gallon', fontsize=15)
    plt.tight_layout()
    plt.savefig('cars/static/cars/image/plot3.png')
    plt.close()

    #plot tansmission
    df['brand'] = df[df['brand'] == brand_input]['brand']
    brand_data = df.dropna()
    counter = collections.Counter(brand_data['transmission'])
    total_count = len(brand_data['transmission'])
    model_count = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    model_count.columns = ['transmission', 'count']
    model_count = model_count.sort_values('transmission', ascending=False)
    indexes = np.arange(len(model_count['transmission']))
    width = 1
    plt.style.use('seaborn-pastel')
    fig, ax = plt.subplots(figsize=(10, 5))
    rects = ax.bar(indexes, model_count['count'], width, edgecolor="grey")
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 1,
                '%.1f%%' % (float(height) * 100 / total_count), ha='center', va='center')
    plt.xticks(indexes, model_count['transmission'],rotation=30, horizontalalignment='right')
    plt.title('Number of ' + brand_input + ' on Sale by transmission', fontsize=18)
    ax.set_xlabel('Transmission', fontsize=15)
    plt.tight_layout()
    plt.savefig('cars/static/cars/image/plot4.png')
    plt.close()

    #plot mileage
    df['brand'] = df[df['brand'] == brand_input]['brand']
    brand_data = df.dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    arr = np.array(brand_data['mileage'])
    arr.sort()
    x=range(1,len(arr)+1)
    plt.plot(x, arr)
    plt.yticks(np.arange(min(arr),max(arr),10000))
    mean = sum(arr)/len(arr)
    plt.axhline(y=mean, ls='dashed')
    ax.text(0.2, mean, "mean = "+str(int(mean)), color='black', fontsize=10,
            bbox=dict(facecolor='wheat', edgecolor='black', boxstyle='round,pad=1'))
    mean = sum(arr) / len(arr)
    ax.set_xlabel('Numbe of '+brand_input +' on Sale', fontsize=15)
    ax.set_ylabel('Mileage', fontsize =15)
    plt.title('Mileage of ' + brand_input + ' on Sale', fontsize=18)
    plt.tight_layout()
    plt.savefig('cars/static/cars/image/plot5.png')
    plt.close()

    return int(result)