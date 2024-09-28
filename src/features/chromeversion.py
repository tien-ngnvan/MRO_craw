
# Import Module 
from win32com.client import *
  
def get_version_number(file_path): 
  
    information_parser = Dispatch("Scripting.FileSystemObject") 
    version = information_parser.GetFileVersion(file_path) 
    return version 
  
if __name__ == "__main__":
    file_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    version = get_version_number(file_path) 
    
    print(version)