from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from base import BaseDataset
import polars as pl


class TBCS(BaseDataset):
    """
    This class is used to crawl and collect data from a web page.
    """

    def __init__(self, url, save_name, get_list):
        """
        Initialize the TBCS instance with the provided URL and save_name.

        :param url: The URL to the web page to crawl.
        :param save_name: The name of the file where the data will be saved.
        """
        self.url = url
        self.save_name = save_name
        self.get_list = get_list # List of keywords to identify specific information
        self.driver = webdriver.Chrome()
        self.link_items = []
        self.title_name = []
        self.category_name = []
        self.sub_category_name = []
        self.classes_name = []
        self.sub_classes_name = []
        self.descrip = []
        self.tech = []
        self.infor = []
        

    def crawl_link_item(self):
        """
        This function finds items on a web page and collects their links.
        """
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
        """
        This function crawls and collects item information from web pages.
        """
        # Maximize the browser window
        self.driver.maximize_window()

        for url in self.link_items:
            # Open the URL in a web browser controlled by a Selenium WebDriver
            self.driver.get(url)
            # Pause execution for 3 seconds to allow the page to load
            sleep(3)

            # Initialize empty lists to store lines and relevant information
            lines = []
            info_list = []

            # Find all elements with the class "product-summary__right"
            elem = self.driver.find_elements(By.CLASS_NAME, "product-summary__right")

            # Iterate through the found elements
            for e in elem:
                # Get the text content of the current element
                info = e.text
                # Append the text with a delimiter (" # ") to the lines list
                lines.append(info + " # ")

                # Split the lines based on newline character '\n'
                for line in lines:
                    a = line.split('\n')

                    # Iterate through the split lines
                    for ele in a:
                        # Check if the line contains keywords from get_list
                        if len(list(set(self.get_list) & (set(ele.split(':'))))):
                            # If it contains a keyword, append it to the info list
                            info_list.append(ele)

            # Initialize an empty list to store group-specific information
            current_item  = []

            # Iterate through the elements in the 'info' list
            for element in info_list:
                # Check if the current element starts with 'Thương hiệu:'
                if element.startswith('Thương hiệu:'):
                    # If it does, and 'current_group' is not empty (indicating the end of a previous group),
                    # then create a mini dictionary from key-value pairs in 'current_group'
                    if current_item :
                        # Create a mini dictionary by splitting each pair on ': ' and forming key-value pairs
                        self.infor.append(current_item)
                    current_item  = [element]
                else:
                    # If the current element does not start with 'Thương hiệu:',
                    # add it to the current group for further processing
                    current_item.append(element)

            # Append the last group as a mini dictionary
            if current_item:
                self.infor.append(current_item)
            
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
        # Create a Polars DataFrame ('df') from multiple lists of data
        df = pl.DataFrame({
            'Category title': self.category_name,
            'Sub-category title': self.sub_category_name,
            'Class title': self.classes_name,
            'Sub-class title': self.sub_classes_name,
            'Title names': self.title_name,
            'Link items': self.link_items,
            'Item description': self.descrip,
            'Item tech': self.tech,
            'Item information': self.infor
        })

        # Convert the 'Item tech' and 'Item information' column to a string representation of a list
        df = df.with_columns(pl.col('Item tech').apply(lambda col: str(col.to_list())))
        df = df.with_columns(pl.col('Item information').apply(lambda col: str(col.to_list())))
        
        # Write the DataFrame to a CSV file specified by 'self.save_name'
        df.write_csv(self.save_name)

        return df
    
    def run(self):
        # Run above functions and return a dataframe
        self.crawl_link_item()
        self.crawl_item_info()
        df = self.save()

        return df

if __name__ == "__main__":
    get_list = ['Thương hiệu', 'Mã hệ thống', 'Model hãng', 'Đơn vị', 'Xuất xứ']
    TBCS = TBCS('https://super-mro.com/thiet-bi-chieu-sang','thietbichieusang.csv',get_list)
    TBCS.run()








