from abc import ABC, abstractclassmethod

class BaseDataset(ABC):   
    @abstractclassmethod
    def crawl_link_item(self):
        pass
    
    @abstractclassmethod
    def crawl_item_info(self):
        pass

    @abstractclassmethod
    def save(self):
        pass

    @abstractclassmethod
    def run(self):
        pass
    
    