from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import random
from time import sleep
from stem import Signal
from stem.control import Controller
import sys

import crawler_backend



## Get actual url (http or https)
def get_url(url):
    if url.startswith('https'):
        url = url[8:]
    if url.startswith('http'):
        url = url[7:]
    page_inserted = requests.get('http://' + url)
    url = page_inserted.url
    
    return url



## Get robots.txt list
def get_robots_list(url):
    url_parse = urlparse(url)
    url_robots = url_parse.scheme+'://'+url_parse.netloc+'/robots.txt'
    robots_list = list()
    temp_list = set()

    res = requests.get(url_robots)
    c = res.content
    soup = BeautifulSoup(c, 'html.parser')

    text = soup.getText()
    lines = text.splitlines()

    for item in lines:
        item = item.strip()
        if item.startswith('Disallow'):
            try:
                pos = item.index('/')
                pos = pos+1
                item = item[pos:]
                temp_list.add(url_parse.scheme+'://'+url_parse.netloc+'/'+item)
            except:
                temp_list.add(item[10:])

    for link in temp_list:
        if '#' in link:
            pos = link.index('#')
            link = link[:pos]
        robots_list.append(link)

    if url in robots_list:
        del robots_list[robots_list.index(url)]

    for link in robots_list:
        if link == '':
            robots_list.remove(link)
        else:
            link = get_url(link)

    return robots_list



## Links retrieval
def get_links(url):
    res = requests.get(url)
    c = res.content
    soup = BeautifulSoup(c, 'html.parser')
    robots_list = get_robots_list(url)

    # Get all types of links and add them in a set
    hrefs = set()
    for link in [h.get('href') for h in soup.find_all('a')]:
        hrefs.add(link)

    temp_list = list(hrefs)

    # Remove all items which may be in robots.txt
    for link in temp_list:
        if link in robots_list:
            temp_list.remove(link)

    # Remove all NoneType items
    for link in temp_list:
        if link is None:
            temp_list.remove(link)

    # Remove all .ico and .css items
    for link in temp_list:
        if link.endswith('.ico') or link.endswith('.css'):
            temp_list.remove(link)

    # Remove all tar.gz, zip and rar items
    for link in temp_list:
        if link.endswith('.tar.gz'):
            temp_list.remove(link)
        if link.endswith('.zip'):
            temp_list.remove(link)
        if link.endswith('.rar'):
            temp_list.remove(link)
            
    # Remove all items of no interest (empty items or pictures)
    for link in temp_list:
        if len(link) < 1:
            temp_list.remove(link)
        if(link.endswith('.png') or link.endswith('.jpg') or link.endswith('.gif') or link.endswith('.exe')):
            temp_list.remove(link)

    # Item filtering and preparation
    links = list()
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    domain = url_parse.netloc
    path = url_parse.path
    query = url_parse.query

    for link in temp_list:
        if domain in link:
            links.append(link)

    for link in temp_list:
        url_parse_link = urlparse(link)
        link_path = url_parse_link.path
        if link_path.startswith('.'):
            link = link[1:]
            if link_path.startswith('.'):
                link = link[1:]
            url_frag = domain+link
            links.append(url_frag)

    for link in temp_list:
        url_parse_link = urlparse(link)
        link_path = url_parse_link.path
        if link_path.startswith('?'):
            url_frag = domain+link
            links.append(url_frag)

    for link in temp_list:
        if link.startswith('//'):
            temp_list.remove(link)

    
    for link in temp_list:
        if link.startswith('//www'):
            temp_list.remove(link)

    for link in temp_list:
        if link.startswith('//www'):
            temp_list.remove(link)

    for link in temp_list:
        url_parse_link = urlparse(link)
        link_path = url_parse_link.path
        if link_path.startswith('./'):
            link = link[1:]
            url_frag = domain+link
            links.append(url_frag)

    for link in temp_list:
        url_parse_link = urlparse(link)
        link_path = url_parse_link.path
        if domain not in link and link_path.startswith('/') and not link.startswith('http') and not link.startswith('www'):
            url_frag = domain+link
            links.append(url_frag)

    for link in temp_list:
        url_parse_link = urlparse(link)
        link_path = url_parse_link.path
        if domain not in link and not link_path.startswith('/') and not link.startswith('http') and not link.startswith('www'):
            if link_path.startswith('./'):
                link = link[2:]
            url_frag = domain+'/'+link
            links.append(url_frag)

    for link in links:
        if 'javascript' in link:
            links.remove(link)
    
    for link in links:
        if 'void' in link:
            links.remove(link)

    for link in links:
        if 'search?' in link:
            links.remove(link)

    for link in links:
        if '#comment'in link:
            links.remove(link)

    for link in links:
        if 'mailto' in link:
            links.remove(link)

    for link in links:
        if '..' in link:
            links.remove(link)

    return links



## Next link retrieval
def get_next_links(url, next_page_style):
    next_links = set()
    temp_links = set()
    # Get all of the links on page
    links = get_links(url)

    # Collect only the links that lead to next pages
    for link in links:
        if 'page.' in link:
            links.remove(link)

    for link in links:
        if '#' not in link:
            temp_links.add(link)

    for link in temp_links:
        if next_page_style in link:
            next_links.add(link)

    next_links = list(next_links)
    
    next_links = [link.replace(link, get_url(link)) for link in next_links]
    next_links = [link.replace(link, no_sid(link)) for link in next_links]

    return next_links



## Get rid of security id if existent in url
def no_sid(url):
    if 'sid=' in url:
        pos = url.index('sid=')
        next_pos = pos+37
        url = url[:pos]+url[next_pos:]
    elif 's=' in url:
        pos = url.index('s=')
        next_pos = pos+37
        url = url[:pos]+url[next_pos:]

    if url.endswith('&'):
        url = url[:-1]
    elif url.endswith('?'):
        url = url[:-1]

    return url



## Change url randomly
def change_url(url):
    links_list = get_links(url)
    index = random.randint(0, len(links_list)-1)
    next_url = links_list[index]
    url = next_url
    url = get_url(url)

    return url



## Find a new url, if there is one
def find_new_url(url):
    page_found_counter = 0
    while True:
        url = change_url(url)
        found = crawler_backend.check_url(url)
        if not found:
            page_found_counter = 0
            url = get_url(url) 
            return url 
        else:
            print('Searching for a new page to crawl... (%s)\n' %url)
            page_found_counter += 1
            if page_found_counter == 30:
                print('\nThere are no more pages to collect')
                sys.exit()
            else:
                continue



## Retrieve the link and its contents
def retrieve_content(url):
    crawler_backend.insert_page(url)
    res = requests.get(url)
    html_code = res.text
    crawler_backend.insert_content(url, html_code)
    print('Crawling: '+url+'\n')



## Text retrieval
def get_text(url):
    res = requests.get(url)
    c = res.content
    soup = BeautifulSoup(c, 'html.parser')
        
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
            
    return page_text



## Check url for errors
def check_error_status(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as err:
        print()
        print (err)
        print()
        return False
    except requests.exceptions.HTTPError as errh:
        print()
        print (errh)
        print()
        return False
    except requests.exceptions.ConnectionError as errc:
        print()
        print (errc)
        print()
        return False
    except requests.exceptions.Timeout:
        print()
        print (errt)
        print()
        return False



## Random crawling
def random_crawl(url, number_of_pages):
    url = get_url(url)
    count = 0
    
    robots_list = get_robots_list(url)
    if url in robots_list:
        print('Not allowed to crawl url: '+url+'\n')
        url = find_new_url(url)
        
    found = crawler_backend.check_url(url)
    if found:
        print(url+' has already been crawled!\n')
        print('Searching for a new page to crawl...\n')
        try:
            url = find_new_url(url)
        except:
            print('Unable to find any valid links\n')
            print('The application will now terminate!\n')
            sys.exit()
        
    while count < number_of_pages:
        try:
            retrieve_content(url)

        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break   

        except:
            check_error_status(url)
            print()
            crawler_backend.insert_content(url, 'ERROR: Page skipped')
            url = find_new_url(url)
            continue

        count += 1

        # Pause after each page
        time = random.randint(1,5)
        sleep(time)

        try:
            url = find_new_url(url)
                
        except:
            break


## Serial crawling
def serial_crawl(url, next_page_style):
    url = get_url(url)
    links_list = list()
    
    robots_list = get_robots_list(url)
    if url in robots_list:
        print('\nNot allowed to crawl url: '+url+'\n')
        sys.exit()
        
    links_list.append(url)

    # Retrieve next page links
    for link in links_list:
        next_links = get_next_links(link, next_page_style)
        links_list.extend(next_link for next_link in next_links if next_link not in links_list)

    # Collect the page content
    for link in links_list:
        try:        
            retrieve_content(link)
            # Pause after each page
            time = random.randint(1,5)
            sleep(time)

        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break   

        except:
            check_error_status(url)
            print()
            crawler_backend.insert_content(url, 'ERROR: Page skipped')
            continue



## Depth crawling
def depth_crawl(url, depth):
    url = get_url(url)
    
    robots_list = get_robots_list(url)
    if url in robots_list:
        print('Not allowed to crawl url: '+url+'\n')
        sys.exit()

    found = crawler_backend.check_url(url)
    if found:
        print(url+' has already been crawled!\n')
        sys.exit()
        
    count = 0
    
    while count < depth:
        count += 1
        print('\nGetting level '+str(count)+' links...\n')
        try:
            if count == 1:
                links_list = get_links(url)
                for link in links_list:
                    retrieve_content(link)
                    # Pause after each page
                    time = random.randint(1,5)
                    sleep(time)
            else:
                for link in links_list:
                    if link == url:
                        pass
                    temp_links = get_links(link)
                    for temp_link in temp_links:
                        if temp_link not in links_list:
                            links_list.append(temp_link)
                            retrieve_content(temp_link)
                            # Pause after each page
                            time = random.randint(1,5)
                            sleep(time)                
        
        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break   

        except:
            check_error_status(url)
            print()
            crawler_backend.insert_content(url, 'ERROR: Page skipped')
            continue
