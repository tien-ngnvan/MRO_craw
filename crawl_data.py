from selenium import webdriver
import numpy as np
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import polars as pl
import os

class Crawl_data:
  
  def __init__(self, url, driver):
    self.url = url
    self.driver = driver
    self.json_form = {
    "subcategory": [],
    "class": [],
    "subclass": [],
    "items": [],
}
  def find_sub_category(self):
    self.driver.get(self.url)
    hrefs_sub_category=self.driver.find_elements(By.CSS_SELECTOR , ".product_category-area__sub-category .item [href]")

    title_sub_categories = [href.text for href in hrefs_sub_category]
    links_sub_categories = [href.get_attribute('href') for href in hrefs_sub_category]

    return  title_sub_categories, links_sub_categories

  def find_classes(self):
    title_sub_categories, links_sub_categories = self.find_sub_category()

    title_classes = []
    link_classes = []

    for i in links_sub_categories:
      self.driver.get(i)
      hrefs_sub_class = self.driver.find_elements(By.CSS_SELECTOR , ".product_category-area__sub-category .item [href]")
      title_classes = [href.text for href in hrefs_sub_class] + title_classes
      link_classes = [href.get_attribute('href') for href in hrefs_sub_class] + link_classes

    return title_classes, link_classes

  def find_subclass(self):
    title_classes, link_classes = self.find_classes()

    title_sub_classes = []
    link_sub_classes = []

    for i in link_classes:
      self.driver.get(i)
      hrefs_item= self.driver.find_elements(By.CSS_SELECTOR , ".product_category-area__sub-category .item [href]")

      text_list = [href.text for href in hrefs_item]
      href_list = [href.get_attribute('href') for href in hrefs_item]

      if href_list == []:
        index = link_classes.index(i)
        title_sub_classes.append(title_classes[index])
        link_sub_classes.append(i)

      title_sub_classes.extend(text_list)
      link_sub_classes.extend(href_list)

    return title_sub_classes, link_sub_classes

  def find_item(self):
    self.driver.get(self.url)
    title_items = []
    link_items = []

    while True:
      try:
        hrefs_item= self.driver.find_elements(By.CSS_SELECTOR , ".product-list .item [href]")
        title_items = [href.text for href in hrefs_item] + title_items
        link_items = [href.get_attribute('href') for href in hrefs_item] + link_items
        # go to next page
        next_pagination_cmt = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
        next_pagination_cmt.click()
        sleep(5)
      except  NoSuchElementException:
        break
    # Create a Polars DataFrame
    df = pl.DataFrame({
        'title_items': title_items,
        'link_items': link_items
    })

    return df

# # Test class
# # Driver path
# chrome_driver_path = 'chromedriver.exe'

# # Add the ChromeDriver path to the system PATH
# os.environ['PATH'] = f'{os.environ["PATH"]};{chrome_driver_path}'

# # Options mặc định
# chrome_options = webdriver.ChromeOptions()

# # Khai báo browser
# driver = webdriver.Chrome(options=chrome_options)

# tbcs = Crawl_data("https://super-mro.com/thiet-bi-chieu-sang", driver)

# df = tbcs.find_item()
# df.head()


