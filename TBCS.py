from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from base import BaseDataset
import polars as pl


class TBCS(BaseDataset):

    def __init__(self,url,save_name):
        self.url = url
        self.driver = webdriver.Chrome()
        self.link_items = []
        self.title_name = []
        self.category_name = []
        self.sub_category_name = []
        self.classes_name = []
        self.sub_classes_name = []
        self.descrip = [] 
        self.tech = []  
        self.save_name = save_name

    def crawl_link_item(self):
        # This function finds items on a web page and collects their links.
        
        # Navigate to the specified URL using the web driver
        self.driver.get(self.url)

        while True:
            try:
                # Find all elements with a 'href' attribute under '.product-list .item'
                hrefs_item = self.driver.find_elements(By.CSS_SELECTOR, ".product-list .item [href]")
                
                # Extract 'href' attribute values and add them to the link_items list
                self.link_items = [href.get_attribute('href') for href in hrefs_item] + self.link_items
                
                # Find and click the 'next' pagination element to go to the next page
                next_pagination_cmt = self.driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
                next_pagination_cmt.click()
                
                # Sleep for 3 seconds to allow the next page to load
                sleep(3)
            except NoSuchElementException:
                # If the 'next' pagination element is not found, exit the loop
                break
        
        # Return the collected item links
        return self.link_items
        
    def crawl_item_info(self):
        self.driver.maximize_window()

        for url in self.link_items:
            self.driver.get(url)
            sleep(3)

             # Extract technical data
            elems = self.driver.find_elements(By.CSS_SELECTOR, '.product-content__technical.pb-34 ul li')
            elems_texts = [e.text.replace('\n', ':') for e in elems]
            self.tech.append(elems_texts[1:])

            # Extract description data
            elem_ = self.driver.find_elements(By.CSS_SELECTOR, '.general_description.css-content.mt-15 p')
            elems = self.driver.find_elements(By.CSS_SELECTOR, ".general_description.css-content.mt-15 h3")

            elems_texts = [f"{i.text.replace('.','')}, {j.text.split(',')[0]}" for i, j in zip(elem_, elems)]
            self.descrip.extend(elems_texts)


            # Find breadcrumb elements on the page
            hrefs_item = self.driver.find_elements(By.CSS_SELECTOR , ".breadcrum .container [href]")

            # Extract text from breadcrumb elements
            title_items = [href.text for href in hrefs_item]
            del title_items[0]

            # Append item details to respective lists
            self.title_name.append(title_items[-1])
            self.category_name.append(title_items[0])

            # Check if there are sub-category, class, and sub-class titles
            if len(title_items) > 2:
                self.sub_category_name.append(title_items[1])
            else:
                self.sub_category_name.append(None)

            if len(title_items) > 3:
                self.classes_name.append(title_items[2])
            else:
                self.classes_name.append(None)

            if len(title_items) > 4:
                self.sub_classes_name.append(title_items[3])
            else:
                self.sub_classes_name.append(None)
        self.driver.quit()

    def save(self):
        df = pl.DataFrame({
            'Category title': self.category_name,
            'Sub-category title': self.sub_category_name,
            'Class title': self.classes_name,
            'Sub-class title': self.sub_classes_name,
            'Title names': self.title_name,
            'Link items': self.link_items,
            'Item description': self.descrip,
            'Item tech': self.tech
        })
        
        df = df.with_columns(pl.col('Item tech').apply(lambda col: str(col.to_list())))
        
        df.write_csv(self.save_name)

        return df
    
    def run(self):
        self.crawl_link_item()
        self.crawl_item_info()
        df = self.save()

        return df

if __name__ == "__main__":
    TBCS = TBCS('https://super-mro.com/thiet-bi-chieu-sang','thietbichieusang.csv')
    TBCS.run()








