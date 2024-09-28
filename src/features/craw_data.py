from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, ElementClickInterceptedException
from multiprocessing.pool import ThreadPool
from base import BaseDataset
from time import sleep
import polars as pl


class Crawler(BaseDataset):
    """
    This class is used to crawl and collect data from a web page.
    """

    def __init__(self, category_link, save_name, get_list, pool_number, item_links_path):
        """
        Initialize the class instance with the provided URL and save_name.

        :param url: The URL to the web page to crawl.
        :param save_name: The name of the file where the data will be saved.
        """

        self.url = category_link
        self.save_name = save_name
        self.get_list = get_list # List of keywords to identify specific information
        self.pool_number = pool_number
        self.item_links_path = item_links_path
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
        # Create a list to store link items
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
        
        # Make sure no link is duplicate
        link_items = list(set(link_items))

        # Return the collected item links
        return link_items
        
    def crawl_item_info(self, url):
        """
        This function crawls and collects item information from web pages.
        """
        # Use Chrome webdriver
        driver = webdriver.Chrome()
        # Open the URL in a web browser controlled by a Selenium WebDriver
        driver.get(url)
        # Pause execution for 3 seconds to allow the page to load
        sleep(3)

        # Append current link to respective lists
        self.link_items.append(url)

        # Find all elements with the class "product-summary__right" which has information in get list
        elem = driver.find_elements(By.CLASS_NAME, "product-summary__right p")
        # Initialize empty lists to store relevant information
        info_list = []
        # Extract description data
        elems_texts = [e.text.replace('\n', ':') for e in elem]
        for info in self.get_list:
            for text in elems_texts:
                if text.startswith(info):
                    info_list.append(text)
        self.infor.append(info_list)

        try:
            see_more_link = driver.find_element(By.CSS_SELECTOR, '.see-more.show a[href]')
            see_more_link.click()
        except NoSuchElementException:
            pass  # Handle if the "see more" link cannot be found
        except ElementClickInterceptedException:
            pass
        except ElementNotInteractableException:
            pass

        # Extract technical data
        elems = driver.find_elements(By.CSS_SELECTOR, '.product-content__technical.pb-34 ul li')
        elems_texts = [e.text.replace('\n', ':') for e in elems]
        self.tech.append(elems_texts[1:])

        # Extract description data
        elem = driver.find_elements(By.CSS_SELECTOR, '.css-content')
        elem_ = driver.find_elements(By.CSS_SELECTOR, '.general_description.css-content.mt-15 p')
        elems = driver.find_elements(By.CSS_SELECTOR, '.general_description.css-content.mt-15 h3')

        elems_texts = [f"{a.text}, {b.text}, {c.text}" for a, b, c in zip(elem, elem_, elems)]
        self.descrip.extend(elems_texts)


        # Find breadcrumb elements on the page
        hrefs_item = driver.find_elements(By.CSS_SELECTOR , ".breadcrum .container [href]")

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
        
        driver.quit()


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
    
    def save_link_items(self):
        # Create a Polars DataFrame ('df') from the list
        link_item = self.crawl_link_item
        df = pl.DataFrame({'Link items': link_item})
        df.write_csv(self.save_name)

        return df

    def run(self):
        # # If you don't have csv file of link items, run this
        # # Crawl the initial links and gather item information
        # link_items = self.crawl_link_item()

        # # (Optional): Save the link items 
        # self.save_link_items()

        web_df = pl.read_csv(self.item_links_path)
        link_items = pl.Series(web_df['Link items']).to_list()

        # Create a thread pool and execute crawl_item_info method for each link item
        pool = ThreadPool(self.pool_number)
        pool.starmap(self.crawl_item_info, [(url, ) for url in link_items])
        pool.close()
        pool.join()

        # Save the collected data and return it as a dataframe
        df = self.save()

        return df

if __name__ == "__main__":

    get_list = ['Thương hiệu', 'Mã hệ thống', 'Model hãng', 'Đơn vị', 'Bảo hành', 'Xuất xứ'] 
    Crawler = Crawler(category_link=None,save_name=r'D:\Private\Work\Program\MRO_craw\output\Craw\vanphongpham.csv', get_list=get_list, pool_number=4, item_links_path=r'D:\Private\Work\Program\MRO_craw\output\Links\vanphongpham.csv')
    Crawler.run()