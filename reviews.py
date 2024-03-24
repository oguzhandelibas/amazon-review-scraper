from selectorlib import Extractor
import requests
import json
import csv
from dateutil import parser as dateparser
import time

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')
MAX_RETRIES = 10
baseUrl = ''

def scrape(url):
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    attempt = 0
    while attempt < MAX_RETRIES:
        # Download the page using requests
        print("Downloading %s (Attempt %d)" % (url, attempt + 1))
        r = requests.get(url, headers=headers)

        # Simple check to check if page was blocked (Usually 503)
        if r.status_code > 500:
            if "To discuss automated access to Amazon data please contact" in r.text:
                print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
            else:
                print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        else:
            # Pass the HTML of the page and create
            extracted_data = e.extract(r.text)


            if extracted_data['reviews']:
                print("Data Scraped Succesfuly at (Attempt %d)" % (attempt + 1))
                return extracted_data


        # Sleep for a moment before the next attempt
        time.sleep(1)
        attempt += 1

    print("Failed to scrape %s after %d attempts" % (url, MAX_RETRIES))
    return None

def save_data(url):
    data = scrape(url)

    if data:
        for r in data['reviews']:
            review_data = {
                "reviewerName": r.get("reviewerName", ""),
                "reviewerText": r.get("reviewerText", ""),
                "overall": r.get("overall", ""),
                "reviewTime": r.get("reviewTime", "")
            }
            print(review_data)
            writer.writerow(review_data)
    else:
        return

# product_data = []
with open("urls.txt", 'r') as urllist, open('data.csv', 'w') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["reviewerID", "asin", "reviewerName", "reviewerText", "overall", "reviewTime"], quoting=csv.QUOTE_ALL)
    writer.writeheader()

    baseUrl = urllist.readlines()[0]
    print(baseUrl)

    i: int
    for i in range(10):
        url = baseUrl + str(i)
        print("Scraping to: %s ..." % url)
        save_data(url)

    #for url in urllist.readlines():
     #   print("Scraping to: %s ..." % url)
      #  save_data(url)


