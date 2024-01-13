import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
import sys
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
# from .. import utils

def scrape(link):
    sys.stdout.reconfigure(encoding='utf-8')

    options = Options()
    options.headless = True

    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)

    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")

    # driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\ZBOOK\anaconda3\Lib\site-packages\bokeh\io\webdriver.py')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(link)

        sleep(7)
    except TimeoutException:
        print("Timed out waiting for page to load")

    page_source = driver.page_source
    soup2 = BeautifulSoup(page_source, 'html.parser')

    title = soup2.find(id='productTitle')
    price_whole = soup2.find(class_='a-price-whole')
    a_price_fraction = soup2.find(class_='a-price-fraction')
    context = ""

    if price_whole and a_price_fraction:
        total_Price = "\nProduct Price: $" + \
            price_whole.text + "" + a_price_fraction.text + "\n"

    if title:
        context = title.text.strip() + total_Price

    context += "\nProduct Overview= "

    productOverview = soup2.find(
        attrs={"data-feature-name":     "productOverview"})
    if productOverview:
        for item in range(len(productOverview.findAll(class_='a-text-bold'))):
            context += productOverview.findAll(class_='a-text-bold')[
                item].text + " : " + productOverview.findAll(class_='po-break-word')[item].text

    context += "\nProduct Details: "

    prodDetTable = soup2.find_all('table', attrs={"role": "presentation"})
    productDetails = soup2.find(
        attrs={"data-feature-name": "detailBullets"})

    if prodDetTable:
        for i in prodDetTable:
            if i:
                context += ' '.join(i.text.encode('ascii',
                                    errors='ignore').decode('ascii').split())

    if productDetails:
        context += ' '.join(productDetails.text.encode('ascii',
                            errors='ignore').decode('ascii').split())

    context += "\nProduct Description: "

    prodDescription = soup2.find(
        attrs={"data-feature-name": "productDescription"})
    if prodDescription:
        context += ' '.join(prodDescription.text.encode('ascii',
                            errors='ignore').decode('ascii').split())

    context += "\nCUSTOMER_REVIEWS=> "

    # reviews = soup2.findAll(attrs={"data-hook": "review"}).find
    # reviews = soup2.findAll(attrs={"class": "review-data"})
    reviews = soup2.findAll(attrs={"data-hook": "review-body"})
    if reviews:
        for review in reviews:
            context += ' '.join(review.text.encode('ascii',   errors='ignore').decode('ascii').split())

    print(context)
    driver.quit()
    return context