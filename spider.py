#######################################################################################
##                                                                                   ##
##   THE APPLICATION GETS A WEB PAGE FROM THE USER, RETURNS THE TEXT FOUND IN IT     ##
##              AND STORES THE RESULTS (URL AND TEXT) IN A DATABASE.                 ##
##                                                                                   ##
##    THE USER IS GIVEN THREE OPTIONS:                                               ##
##    1. RANDOM CRAWLING - CHOOSE RANDOM LINKS UNTIL A NUMBER OF PAGES IS REACHED    ##
##    2. SERIAL CRAWLING - FOLLOW ONLY THE NEXT-PAGE LINKS                           ##
##    3. BREADTH-BASED CRAWLING - CRAWL ALL PAGES BASED ON A CERTAIN DEPTH CHOSEN    ##
##                                                                                   ##
#######################################################################################


from time import sleep
import os
import crawler_backend
import crawler_functions as function



# Check to see if there is a database in progress...
check = crawler_backend.view()

if len(check) != 0:
    print('\nAn active data collection progress is found\n')
    print('OPTIONS')
    print('- Press 1 to create a new file and start a fresh crawl')
    print('- Any key to continue current collection')
    choice = input('\nUser input: ')
    if choice == '1':
        os.remove('crawler_database.db')
        print('\nRemoving file...\n')
        sleep(1)
        print('File removed!\n')
        crawler_backend.connect()
    else:
        print()
        

while True:
    # Get the initial page from the user
    print('OPTIONS')
    print('1 - Random Crawl')
    print('2 - Serial Crawl')
    print('3 - Breadth-first Crawl')
    print('4 - Quit')
    
    choice = input('\nUser input: ')
    
    if len(choice) < 1:
        print("\nYou haven't typed anything!\n")
        continue
    
    if (choice == '1'):
        url = input('\nEnter a URL: ')
        url = function.get_url(url)
        if function.check_error_status(url):
            pass
        else:
            continue
        number_of_pages = int(input('How many pages do you wish to crawl? : '))
        if number_of_pages < 1:
            print('\nSorry to see you go.')
            break
        crawler_backend.connect()
        print('\nProcessing...\n')
        sleep(1)
        function.random_crawl(url, number_of_pages)

    elif (choice == '2'):
        url = input('\nEnter a URL: ')
        url = function.get_url(url)
        next_page_style = input('\nEnter the next page style (eg. page=2): ')
        if function.check_error_status(url):
            pass
        else:
            continue
        crawler_backend.connect()
        print('\nProcessing...\n')
        sleep(1)
        print('Collecting the URLs...\n')
        function.serial_crawl(url, next_page_style)
        
    elif (choice == '3'):
        url = input('\nEnter a URL: ')
        url = function.get_url(url)
        if function.check_error_status(url):
            pass
        else:
            continue
        print('\nIMPORTANT NOTE: Depth equal or greater than 2 will require a significant amount of time to complete.\n')
        depth = int(input('Please choose the depth: '))
        if depth < 1:
            print('\nSorry to see you go.')
            break
        if depth > 3:
            print('This is a very high selection, it will take some time!')
        crawler_backend.connect()
        print('\nProcessing...\n')
        sleep(1)
        function.depth_crawl(url, depth)
        
    elif (choice == '4'):
        print('\nHave a nice day!\n')
        break
    
    else:
        print('This is not a valid selection!\n')
        continue
    
    print('Done!\n')
    break
