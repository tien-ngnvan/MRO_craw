from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import numpy as np
import polars as pl
import os

class CrawlData:

  def __init__(self, url, driver):
    self.url = url
    self.driver = driver

  def find_sub_category(self):
    # This function find the sub-categories
    # Visit the specified URL
    self.driver.get(self.url)
    
    # Find sub-categories using CSS Selector
    hrefs_sub_category = self.driver.find_elements(By.CSS_SELECTOR, ".product_category-area__sub-category .item [href]")

    # Extract title and links for sub-categories
    title_sub_categories = [href.text for href in hrefs_sub_category]
    links_sub_categories = [href.get_attribute('href') for href in hrefs_sub_category]

    return title_sub_categories, links_sub_categories

  def find_classes(self):
    # This function find the classes
    # Get sub-category data
    title_sub_categories, links_sub_categories = self.find_sub_category()
    
    title_classes = []
    link_classes = []

    for i in links_sub_categories:
      # Visit sub-category URL
      self.driver.get(i)
      
      # Find sub-classes using CSS Selector
      hrefs_sub_class = self.driver.find_elements(By.CSS_SELECTOR, ".product_category-area__sub-category .item [href]")

      title_classes = [href.text for href in hrefs_sub_class] + title_classes
      link_classes = [href.get_attribute('href') for href in hrefs_sub_class] + link_classes

    return title_classes, link_classes

  def find_subclass(self):
    # This function find the sub-classes
    # Get class data
    title_classes, link_classes = self.find_classes()

    title_sub_classes = []
    link_sub_classes = []

    for i in link_classes:
      # Visit class URL
      self.driver.get(i)
      
      # Find items using CSS Selector
      hrefs_item = self.driver.find_elements(By.CSS_SELECTOR, ".product_category-area__sub-category .item [href]")

      text_list = [href.text for href in hrefs_item]
      href_list = [href.get_attribute('href') for href in hrefs_item]

      # If the classes have no sub-classes, then use it instead
      if href_list == []:
        index = link_classes.index(i)
        title_sub_classes.append(title_classes[index])
        link_sub_classes.append(i)

      title_sub_classes.extend(text_list)
      link_sub_classes.extend(href_list)

    return title_sub_classes, link_sub_classes

  def find_item(self):
    # This function finds items on a web page and collects their links.
    
    # Navigate to the specified URL using the web driver
    self.driver.get(self.url)
    
    # Initialize a list to store item links
    link_items = []

    while True:
        try:
            # Find all elements with a 'href' attribute under '.product-list .item'
            hrefs_item = self.driver.find_elements(By.CSS_SELECTOR, ".product-list .item [href]")
            
            # Extract 'href' attribute values and add them to the link_items list
            link_items = [href.get_attribute('href') for href in hrefs_item] + link_items
            
            # Find and click the 'next' pagination element to go to the next page
            next_pagination_cmt = self.driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
            next_pagination_cmt.click()
            
            # Sleep for 3 seconds to allow the next page to load
            sleep(3)
        except NoSuchElementException:
            # If the 'next' pagination element is not found, exit the loop
            break
    
    # Return the collected item links
    return link_items

if __name__ == "__main__":
    # Driver path
    chrome_driver_path = 'chromedriver.exe'
    
    # Add the ChromeDriver path to the system PATH
    os.environ['PATH'] = f'{os.environ["PATH"]};{chrome_driver_path}'

    # Options default
    chrome_options = webdriver.ChromeOptions()

    # Create driver
    driver = webdriver.Chrome(options=chrome_options)

    tbcs = CrawlData("https://super-mro.com/phu-kien-kim-khi", driver)

    # Get item links using the 'find_item' function
    link_items = tbcs.find_item()

    # Define a function to create lists of item details
    def create_lists(driver, link_items):
        # Initialize empty lists to store item details
        title_name = []
        category_name = []
        sub_category_name = []
        classes_name = []
        sub_classes_name = []

        # Loop through each item link
        for i in link_items:
            # Navigate to the item's page
            driver.get(i)
            sleep(2)
            
            # Find breadcrumb elements on the page
            hrefs_item = driver.find_elements(By.CSS_SELECTOR , ".breadcrum .container [href]")

            # Extract text from breadcrumb elements
            title_items = [href.text for href in hrefs_item]
            del title_items[0]

            # Append item details to respective lists
            title_name.append(title_items[-1])
            category_name.append(title_items[0])

            # Check if there are sub-category, class, and sub-class titles
            if len(title_items) > 2:
                sub_category_name.append(title_items[1])
            else:
                sub_category_name.append(None)

            if len(title_items) > 3:
                classes_name.append(title_items[2])
            else:
                classes_name.append(None)

            if len(title_items) > 4:
                sub_classes_name.append(title_items[3])
            else:
                sub_classes_name.append(None)

        # Return lists containing item details
        return title_name, category_name, sub_category_name, classes_name, sub_classes_name

    # Call the 'create_lists' function to extract item details
    title_name, category_name, sub_category_name, classes_name, sub_classes_name = create_lists(driver, link_items)

    # Create a DataFrame using the extracted item details
    df = pl.DataFrame({
        'Title names': title_name,
        'Link items': link_items,  # Note: link_items is not defined here, consider using 'links' instead
        'Category title': category_name,
        'Sub-category title': sub_category_name,
        'Class title': classes_name,
        'Sub-class title': sub_classes_name
    })

    # Write the DataFrame to a CSV file
    df.write_csv('Dataframe.csv')




