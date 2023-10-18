from unstructured.cleaners.core import clean
from unstructured.partition.html import partition_html
from unstructured.cleaners.core import clean_non_ascii_chars
from unstructured.cleaners.core import clean_postfix, clean_prefix
from unstructured.cleaners.core import clean_trailing_punctuation
from unstructured.cleaners.core import remove_punctuation
from unstructured.cleaners.core import replace_unicode_quotes
import polars as pl


# Define a class for text cleaning
class TextClean:
    def __init__(self, texts):
        self.texts = texts
        self.cleaned_texts = []


    def clean_tag_html(self,text):
        # Method to clean HTML tags and extract text
        assert isinstance(text, str), 'Input should be a string'
        elements = partition_html(text=text)
        return elements[0].text

    def clean_text(self, text):
        # Method to clean text (removing bullets, extra whitespace, etc.)
        clean_text = clean(text, bullets=True, extra_whitespace=True, dashes=False, lowercase=False)
        return clean_text

    def clean_postfix(self, text):
        # Method to clean postfix content
        clean_text = clean_postfix(text, pattern=r"(END|STOP)")
        return clean_text

    def clean_prefix(self, text):
        # Method to clean prefix content
        clean_text = clean_prefix(text, pattern=r"(SUMMARY|DESCRIPTION):")
        return clean_text

    def clean_trailing_punctuation(self, text):
        # Method to remove trailing punctuation
        clean_text = clean_trailing_punctuation(text)
        return clean_text

    def remove_punctuation(self, text):
        # Method to remove all punctuation
        clean_text = remove_punctuation(text)
        return clean_text

    def replace_unicode_quotes(self, text):
        # Method to replace Unicode quotes with ASCII quotes
        clean_text = replace_unicode_quotes(text)
        return clean_text
    
    def remove_texts(self, text):
        # Method to remove nonsense information
        start_index = text.find(", Đại siêu thị Vật")

        # If the string is found, remove it along with the following text
        if start_index != -1:
            result = text[:start_index]
        else:
            # If the string is not found, leave the text unchanged
            result = text
        return result
    
    def process(self):
        # Clean every text in the list with all process function
        for text in self.texts:
            text = self.clean_tag_html(text)
            text = self.clean_postfix(text)
            text = self.clean_prefix(text)
            text = self.clean_text(text)
            text = self.replace_unicode_quotes(text)
            text = self.remove_texts(text)
            self.cleaned_texts.append(text)

    def save(self):
        # Save the cleaned list to a csv file
        df = pl.DataFrame({'Text clean': self.cleaned_texts})
        df.write_csv('textclean.csv')

    def run(self):
        # Make sure input is a list
        assert isinstance(self.texts, list), 'Input should be a list'
        # Run the process function
        self.process()
        # Run the save function
        self.save()
        
        return self.cleaned_texts
    
if __name__ == "__main__":
    # Read the contents of the CSV file using pandas
    web_df = pl.read_csv(r'D:\Private\Work\Program\MRO_craw\output\Craw\vanphongpham.csv')

    # Extract the 'Item information' column from the DataFrame and convert it to a list
    info_items = pl.Series(web_df['Item description']).to_list()

    # Create an instance of TextClean and clean the HTML tags
    Cleaner = TextClean(info_items)
    cleaned_html = Cleaner.run()