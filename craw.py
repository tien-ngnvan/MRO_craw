import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from time import sleep
import random
import os


class CrawlProduct(object):

    def __init__(self, web_urls):
        self.web_urls = web_urls
        self.descrip = [] 
        self.detail = []
        self.tech = []       
    
    def crawl_descrip(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        for url in self.web_urls:
            driver.get(url)
            sleep(5)

            elems = driver.find_elements(By.ID, "mcetoc_1gmsokuk60")
            elem_texts = [elem.text.split(',')[0] for elem in elems]
            self.detail.extend(elem_texts)

            elem_ = driver.find_element(By.CSS_SELECTOR, '.general_description.css-content.mt-15 p')
            self.descrip.append(elem_.text)
        driver.quit()

    def crawl_tech(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        for url in self.web_urls:
            driver.get(url)
            sleep(5)

            elems = driver.find_elements(By.CSS_SELECTOR, '.product-content__technical.pb-34 ul li')
            elems_texts = [e.text.replace('\n', ':') for e in elems]
            self.tech.append(elems_texts[1:])
        driver.quit()



if __name__ == "__main__":

    # df = pd.read_csv('thietbichieusang.csv')
    # web_urls = [i for i in df['link_items'].values]
    # web_urls = web_urls[:5]
    # print(web_urls)

    # CrawlProduct = CrawlProduct(web_urls)
    # CrawlProduct.crawl_tech()
    # print(CrawlProduct.tech)



       
        