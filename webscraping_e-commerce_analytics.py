#run in terminal

#pip install --upgrade pip
#pip install requests
#pip install beautifulsoup4
#pip install pandas
#pip install matplotlip
#pip install streamlit
#pip install selenium
#pip install textblob
#streamlit run webscraping_e-commerce_analytics.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)


# Setup WebDriver for dynamic pages (e.g., Amazon, eBay, AliExpress, Walmart)
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run headless to prevent UI from opening
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# Function to fetch Amazon product details
def scrape_amazon(url, headless=True):
    logging.info(f"Scraping Amazon URL: {url}")
    driver = setup_driver(headless)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle")))
    except Exception as e:
        logging.error(f"Error while loading the page: {e}")
        driver.quit()
        return {"title": None, "price": None, "rating": None, "url": url}

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("span", {"id": "productTitle"}).text.strip()
    except AttributeError:
        title = None

    try:
        price = soup.find("span", {"id": "priceblock_ourprice"}).text.strip()
    except AttributeError:
        price = None

    try:
        rating = soup.find("span", {"id": "acrPopover"}).text.strip()
    except AttributeError:
        rating = None

    logging.info(f"Scraped data - Title: {title}, Price: {price}, Rating: {rating}")

    driver.quit()

    return {"title": title, "price": price, "rating": rating, "url": url}


# Function to fetch eBay product details
def scrape_ebay(url, headless=True):
    logging.info(f"Scraping eBay URL: {url}")
    driver = setup_driver(headless)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1 span span")))
    except Exception as e:
        logging.error(f"Error while loading the page: {e}")
        driver.quit()
        return {"title": None, "price": None, "rating": None, "url": url}

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "x-item-title__mainTitle"}).text.strip()
    except AttributeError:
        title = None

    try:
        price = soup.find("span", {"class": "x-price-primary"}).text.strip()
    except AttributeError:
        price = None

    try:
        rating = soup.find("div", {"class": "x-star-rating"}).text.strip()
    except AttributeError:
        rating = None

    logging.info(f"Scraped data - Title: {title}, Price: {price}, Rating: {rating}")

    driver.quit()

    return {"title": title, "price": price, "rating": rating, "url": url}


# Function to fetch AliExpress product details
def scrape_aliexpress(url, headless=True):
    logging.info(f"Scraping AliExpress URL: {url}")
    driver = setup_driver(headless)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-title-text")))
    except Exception as e:
        logging.error(f"Error while loading the page: {e}")
        driver.quit()
        return {"title": None, "price": None, "rating": None, "url": url}

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "product-title-text"}).text.strip()
    except AttributeError:
        title = None

    try:
        price = soup.find("span", {"class": "product-price-value"}).text.strip()
    except AttributeError:
        price = None

    try:
        rating = soup.find("div", {"class": "feedback-ratings"}).text.strip()
    except AttributeError:
        rating = None

    logging.info(f"Scraped data - Title: {title}, Price: {price}, Rating: {rating}")

    driver.quit()

    return {"title": title, "price": price, "rating": rating, "url": url}


# Function to fetch Walmart product details
def scrape_walmart(url, headless=True):
    logging.info(f"Scraping Walmart URL: {url}")
    driver = setup_driver(headless)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.prod-ProductTitle")))
    except Exception as e:
        logging.error(f"Error while loading the page: {e}")
        driver.quit()
        return {"title": None, "price": None, "rating": None, "url": url}

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "prod-ProductTitle"}).text.strip()
    except AttributeError:
        title = None

    try:
        price = soup.find("span", {"class": "price-group"}).text.strip()
    except AttributeError:
        price = None

    try:
        rating = soup.find("span", {"class": "ReviewsHeader-ratingPrefix"}).text.strip()
    except AttributeError:
        rating = None

    logging.info(f"Scraped data - Title: {title}, Price: {price}, Rating: {rating}")

    driver.quit()

    return {"title": title, "price": price, "rating": rating, "url": url}


# Main function to scrape data
def scrape_data(ecommerce_site, urls):
    data = []

    for url in urls:
        if ecommerce_site == 'Amazon':
            data.append(scrape_amazon(url))
        elif ecommerce_site == 'eBay':
            data.append(scrape_ebay(url))
        elif ecommerce_site == 'AliExpress':
            data.append(scrape_aliexpress(url))
        elif ecommerce_site == 'Walmart':
            data.append(scrape_walmart(url))

        time.sleep(2)  # To avoid getting blocked by websites

    return pd.DataFrame(data)


# Data cleaning function
def clean_data(df):
    df['price'] = df['price'].apply(lambda x: re.sub(r'[^\d.]', '', str(x)) if x is not None else None)
    df['rating'] = df['rating'].apply(lambda x: re.sub(r'[^\d.]', '', str(x)) if x is not None else None)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    return df


# Visualization function for price trends
def visualize_price_trends(df):
    plt.figure(figsize=(10, 6))
    plt.plot(df['title'], df['price'], marker='o', linestyle='-', color='b')
    plt.title("Price Trends Across Products")
    plt.xlabel("Product")
    plt.ylabel("Price")
    plt.xticks(rotation=90)
    plt.show()


# Streamlit Web Interface
def main():
    st.title("E-commerce Product Data Scraper")

    ecommerce_sites = ['Amazon', 'eBay', 'AliExpress', 'Walmart']

    st.sidebar.header("Select E-commerce Website")
    ecommerce_site = st.sidebar.selectbox("Select the Website to Scrape", ecommerce_sites)

    st.sidebar.header("Enter Product URLs")
    urls = st.sidebar.text_area("Enter Product URLs (comma separated)").split(',')

    if st.sidebar.button("Scrape Data"):
        if urls:
            st.write(f"Scraping {len(urls)} products from {ecommerce_site}...")
            df = scrape_data(ecommerce_site, urls)
            st.write("Scraped Data Preview:")
            st.write(df.head())

            # Clean data
            df_cleaned = clean_data(df)
            st.write("Cleaned Data Preview:")
            st.write(df_cleaned.head())

            # Visualize price trends
            st.write("Price Trends Visualization:")
            visualize_price_trends(df_cleaned)

        else:
            st.warning("Please enter at least one URL to scrape.")


if __name__ == "__main__":
    main()

#streamlit run webscraping_e-commerce_analytics.py