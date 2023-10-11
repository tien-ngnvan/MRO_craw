from unstructured.cleaners.core import clean
from unstructured.partition.html import partition_html
from unstructured.cleaners.core import clean_non_ascii_chars
from unstructured.cleaners.core import clean_postfix, clean_prefix
from unstructured.cleaners.core import clean_trailing_punctuation
from unstructured.cleaners.core import remove_punctuation
from unstructured.cleaners.core import replace_unicode_quotes


class TextClean:
    def __init__(self, text):
        self.text = text

    def clean_tag_html(self):
        elements = partition_html(text=self.text)
        
        return elements[0].text
    
    def clean_text(self):
        clean_text = clean(self.text, bullets=True, extra_whitespace=True, dashes=True, lowercase=True)

        return clean_text
    
    def clean_non_ascii_chars(self):
        clean_text = clean_non_ascii_chars(self.text)

        return clean_text
    
    def clean_postfix(self):
        clean_text = clean_postfix(self.text)

        return clean_text
    
    def clean_prefix(self):
        clean_text = clean_prefix(self.text)

        return clean_text
    
    def clean_trailing_punctuation(self):
        clean_text = clean_trailing_punctuation(self.text)

        return clean_text
    
    def remove_punctuation(self):
        clean_text = remove_punctuation(self.text)

        return clean_text
    
    def replace_unicode_quotes(self):
        clean_text = replace_unicode_quotes(self.text)

        return clean_text
    
if __name__ == '__main__':
    text = '"\n<html charset="utf-8"><p>Hello 😀</p></html>"'
    Cleaner = TextClean(text)
    print(Cleaner.clean_tag_html())