import pandas as pd
import urllib
import json
import urllib.request
import csv
from datetime import date
from google.cloud import storage


def cupstringCSV(data, context):
    # Read CSV file with all SKUS, this is only for SKU (AttribureNumber)
    df = pd.read_csv(
        r'https://transport.productsup.io/7a6c5b87a8c1bf44e114/channel/262099/noimages.csv')
    saved_column = df.ArticleNumber
    i = 0

    # CSV header is static, if we want to add more variables to the file we need to add to the header first

    header = ['Sku', 'CupString', 'Price', 'Was Price']

    # Declaring todays date to create unique daily file name

    today = date.today()
    print("Today's date:", today)
    print(df.shape)
    # Create CSV file and write header,
    # added "new line =  null" because it was printing out a empty line after every new row

    with open('/tmp/file-' + str(today) + '.csv', 'w', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        # created for loop to iterate through every single sku number in the given CSV

        for sku in saved_column:
            try:
                # This will replace every URL with the new URL containing the SKU we have pulled from the CSV
                url = "https://www.woolworths.com.au/apis/ui/product/detail/{}".format(
                    saved_column[i]).replace('.0', '')
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())
                print(str(data["Product"]["Stockcode"]) + "," + data["Product"]["CupString"] +
                      "," + str(data["Product"]["Price"]) + "," + str(data["Product"]["WasPrice"]))

                # This created variables we can write into our new CSV that will be then sent to productsUp
                sku = str(data["Product"]["Stockcode"])
                cupstring = data["Product"]["CupString"]
                price = str(data["Product"]["Price"])
                wasprice = str(data["Product"]["WasPrice"])
                writer.writerow([sku, cupstring, price, wasprice])
                i += 1
            except Exception as err:
                # This handles any errors for SKUs that require login (alcohol & tabacco)
                print(err)
                i += 1
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('kr_cupstring')
    blob = bucket.blob('cupstring.csv')
    # df.to_csv('/tmp/cupstring.csv')
    blob.upload_from_filename('/tmp/file-' + str(today) + '.csv')
