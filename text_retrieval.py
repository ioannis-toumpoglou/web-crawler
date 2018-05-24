from bs4 import BeautifulSoup

import crawler_backend
import crawler_functions as function



## Text retrieval
def get_text(content):
    soup = BeautifulSoup(content, 'html.parser')
        
    # Ignore all script and style elements
    for script in soup(['script','style','head','title','meta','[document]']):
        script.extract()

    # Get text and break into lines
    text = soup.getText()
    lines = text.splitlines()

    # Iterate the text lines
    page_text = list()
    for item in lines:
        item = item.strip()     # Remove spaces surrounding text
        if item == " " or item == "":       # Ignore blank items
            pass
        if len(item) > 30:      # Filter the items by length
            page_text.append(item)

    page_text = '\n\n'.join(page_text)
            
    return page_text


records = crawler_backend.page_content()

for record in records:
    url = record[1]
    html_code = record[2]
    text = get_text(html_code)
    crawler_backend.insert_text(url, text)

print('Text retrieved!')
