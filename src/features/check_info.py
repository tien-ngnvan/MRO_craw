from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from time import sleep
import polars as pl


class CrawInfo(object):
    def __init__(self, url, save_name) -> None:
        """
        Initializes an instance of CrawInfo.

        :param url: The URL of the webpage to scrape.
        :param save_name: The name of the CSV file to save the scraped data.
        """
        # Initialize class attributes
        self.url = url
        self.save_name = save_name
        self.driver = webdriver.Chrome()
        self.linkk = []  # List to store links
        self.category = []  # List to store category titles
        self.sub_category = []  # List to store sub-category titles
        self.title_class = []  # List to store class titles
        self.info_subclass = []  # List to store information from sub-classes

    def get_link_subclass(self):
        """
        Scrapes links to sub-categories from the main page.
        """
        self.driver.get(self.url)
        sleep(3)

        item = self.driver.find_elements(By.CSS_SELECTOR, '.product_category-area__sub-category .item a[href]')
        link = [i.get_attribute('href') for i in item]
        # Get links to sub-class
        for url in link:
            self.driver.get(url)
            sleep(2)
            item = self.driver.find_elements(By.CSS_SELECTOR, '.product_category-area__sub-category .item a[href]')
            link = [i.get_attribute('href') for i in item]
            self.linkk.extend(link)

        self.driver.quit()

    def get_info(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        for url in self.linkk:
            driver.get(url)
            sleep(3)

            # Find breadcrumb elements on the page
            hrefs_item = driver.find_elements(By.CSS_SELECTOR, '.breadcrum .container [href]')

            # Extract text from breadcrumb elements and cut off the first elem
            item = [i.text for i in hrefs_item]
            del item[0]

            #take category
            self.category.append(item[0])

            #take sub_category and class
            if len(item) > 1:
                self.sub_category.append(item[1])
            else:
                self.sub_category.append(None)

            if len(item) > 2:
                self.title_class.append(item[2])
            else:
                self.title_class.append(None)

            try:
                see_more_link = driver.find_element(By.CSS_SELECTOR, '.see-more.show a[href]')
                see_more_link.click()
            except NoSuchElementException:
                pass # Handle if the "see more" link cannot be found
            except ElementClickInterceptedException:
                pass

            # find info sub-class
            elem = driver.find_elements(By.CSS_SELECTOR, '.css-content')
            text = [e.text for e in elem]
            self.info_subclass.append(text)

        driver.quit()

    def save(self):
        # Create a Polars DataFrame ('df') from multiple lists of data
        df = pl.DataFrame({
            'Link Subclass' : self.linkk,
            'Category Title': self.category,
            'Sub-category Title': self.sub_category,
            'Class Title' : self.title_class,
            'Information' : self.info_subclass        
        })

        # Convert the 'Information' column to a string representation of a list
        df = df.with_columns(pl.col('Information').apply(lambda col: str(col.to_list())))

        # Write the DataFrame to a CSV file specified by 'self.save_name'
        df.write_csv(self.save_name)
        return df

    def run(self):
        self.get_link_subclass()
        print(CrawInfo.linkk)
        self.get_info()
        df = self.save()

        return df
    
# Entry point for the script
if __name__ == "__main__":

    # CrawInfo = CrawInfo(url='https://super-mro.com/thiet-bi-chieu-sang', save_name='thietbichieusang_test.csv')
    # CrawInfo.run()