from unstructured.cleaners.core import clean
from unstructured.partition.html import partition_html
from unstructured.cleaners.core import clean_non_ascii_chars
from unstructured.cleaners.core import clean_postfix, clean_prefix
from unstructured.cleaners.core import clean_trailing_punctuation
from unstructured.cleaners.core import remove_punctuation
from unstructured.cleaners.core import replace_unicode_quotes


# Define a class for text cleaning
class TextClean:
    def __init__(self, text):
        self.text = text

    # Method to clean HTML tags and extract text
    def clean_tag_html(self):
        elements = partition_html(text=self.text)
        return elements[0].text

    # Method to clean text (removing bullets, extra whitespace, etc.)
    def clean_text(self):
        clean_text = clean(self.text, bullets=True, extra_whitespace=True, dashes=True, lowercase=True)
        return clean_text

    # Method to remove non-ASCII characters
    def clean_non_ascii_chars(self):
        clean_text = clean_non_ascii_chars(self.text)
        return clean_text

    # Method to clean postfix content
    def clean_postfix(self):
        clean_text = clean_postfix(self.text)
        return clean_text

    # Method to clean prefix content
    def clean_prefix(self):
        clean_text = clean_prefix(self.text)
        return clean_text

    # Method to remove trailing punctuation
    def clean_trailing_punctuation(self):
        clean_text = clean_trailing_punctuation(self.text)
        return clean_text

    # Method to remove all punctuation
    def remove_punctuation(self):
        clean_text = remove_punctuation(self.text)
        return clean_text

    # Method to replace Unicode quotes with ASCII quotes
    def replace_unicode_quotes(self):
        clean_text = replace_unicode_quotes(self.text)
        return clean_text

if __name__ == '__main__':
    # Sample text containing HTML and emojis
    text = '"\n<html charset="utf-8"><p>Hello 😀</p></html>"'

    # Create an instance of TextClean and clean the HTML tags
    Cleaner = TextClean(text)
    cleaned_html = Cleaner.clean_tag_html()
    print(cleaned_html)