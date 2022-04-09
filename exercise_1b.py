import csv
import os
import re
import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def csv_generator(atm_list, city, atm_name=None):
    ## Output to a csv file
    filename = f'./CITY/{city}/ATM_FILES/CSV/consolidated_atm_list.csv'
    with open(filename, 'w', newline='\n') as atm_file:
        fieldnames = ['ATM','Heading', 'Operator', 'Contact Details', 'email', 'City', 'Location', 'Address', 'Type', 'Fiat', 'Supported Coins']
        atm_writer = csv.DictWriter(atm_file, delimiter=',',fieldnames=fieldnames)
        atm_writer.writeheader()
        # atm_writer.writerow(atm_list) #Uncomment and add a function call in get_atm_details() with atm_details, city, atm_name params to use this to generate csv for each and every city
        for values in atm_list.values():
            atm_writer.writerow(values)
        atm_file.close()
    return True
            
def get_atm_details(city, atm_name, url=None, driver=None):
    atm_details = {}
    
    #Make a call to the atm details page]
    script = f'window.open(\'{url}\')'
    driver.execute_script(script)
    time.sleep(7)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    
    #Store the specific atm page for logging/debugging and close the current window
    filename = f'./CITY/{city}/ATM_FILES/HTML/{atm_name}.html'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(driver.page_source)
        f.close()
        driver.close()
    time.sleep(7)
        
    #Process the file using bs4
    with open(f'{filename}', 'r') as sf:
        file_soup = BeautifulSoup(sf, 'lxml')
        sf.close()
    
        
    #Heading
    heading = file_soup.find('h1').text
    
    #Operator details
    operator_fieldset = file_soup.find_all('fieldset')[1]
    operator_name = operator_fieldset.find('span', class_='glyphicon2 glyphicon2-briefcase').parent.parent.text.split(":")[1].strip()
    phn_sms_wa_op_fieldset = file_soup.find_all(href=re.compile("tel:|sms:|//wa.me/"))
    contact_details = { i['href'].split(':')[1] for i in phn_sms_wa_op_fieldset }
    mail_id = file_soup.find(href=re.compile("mailto:"), string=True).text
    
    #Location details
    location_fieldset = file_soup.find_all('fieldset')[2]
    city = location_fieldset.find('span', class_='glyphicon2 glyphicon2-map').parent.parent.text.split(":")[1].strip()
    location = location_fieldset.find('span', class_='glyphicon2 glyphicon2-shop_window').parent.parent.text.split(":")[1].strip()
    address = location_fieldset.find('span', class_='glyphicon2 glyphicon2-google_maps').parent.parent.text.split(":")[1]  
    
    #Machine details
    machine_details_fieldset = file_soup.find_all('fieldset')[3]
    atm_type = machine_details_fieldset.find('span', class_='glyphicon2 glyphicon2-building').parent.parent.text.split(":")[1].strip()
    supported_fiat = machine_details_fieldset.find('tr', class_='fiat').find('td', class_='centered').text
    supported_coins_list = machine_details_fieldset.find('tbody').find_all('td', class_=False)
    supported_coins = [ supported_coins_list[i].text.strip() for i in range(len(supported_coins_list)-1) ]
    
    atm_details['ATM'] = atm_name
    atm_details['Heading'] = heading
    atm_details['Operator'] = operator_name
    atm_details['Contact Details'] = contact_details
    atm_details['email'] = mail_id
    atm_details['City'] = city
    atm_details['Location'] = location
    atm_details['Address'] = address
    atm_details['Type'] = atm_type
    atm_details['Fiat'] = supported_fiat
    atm_details['Supported Coins'] = supported_coins
    # csv_generator(atm_details, city, atm_name)
    return atm_details

def get_atm_url():
    while(True):
        user_input = input(f'Please enter 1/2:\n1)Birmingham\n2)Birmingham US\n')
        if int(user_input) == 1:
            url = 'https://coinatmradar.com/city/3848/bitcoin-atm-birmingham/'
            city = 'Birmingham'
            break
        elif int(user_input) == 2:
            url = 'https://coinatmradar.com/city/208/bitcoin-atm-birmingham-us/'
            city = 'Birmingham_US'
            break
        else:
            print("Please enter either 1 or 2")
    print(f'City Selected for scraping: {city}')
            
    # Options argument to allow opening of new tabs -- Enable popups
    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = uc.Chrome(options = chrome_options)
    driver.maximize_window()
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(10)

    #Get the number of atm machines to list all the atm in the place
    atm_number = driver.find_element(by=By.XPATH, value='/html/body/div[3]/div/div/div/div[1]/h6').text
    atm_number = atm_number.split(':')[1].strip()
    first_window = driver.window_handles[0]
    
    #Loading more chunks to get all the data
    num = 12 #default
    while num < int(atm_number):
        x_path_value = '/html/body/div[3]/div/div/div/div[6]/div[{}]/a'.format(num)
        load_more = driver.find_element(by=By.XPATH, value=x_path_value)
        load_more.click()
        num+=10
        time.sleep(7)

    #Store the file for use with bs4
    try:
        filename = f'./CITY/{city}/HTML/{city}.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
                f.write(driver.page_source)
        with open(filename, 'r') as sf:
            soup = BeautifulSoup(sf, 'lxml')
    except Exception:
        print(Exception)
        print("File not present or Permission Error")
    ## Closes the file descriptor --- always
    finally:
        f.close()
        sf.close()
        
    details_url = soup.find_all('div', class_='atm-item clearfix is-current')
    atm_list = {}
    for idx, is_current_class in enumerate(details_url):
        driver.switch_to.window(first_window)
        atm_name = is_current_class.find('div', class_='place').text.strip()
        atm_url = is_current_class.find('div', class_='place').a['href'].strip()
        atm_list.update({idx:get_atm_details(city, atm_name, atm_url, driver)})
        
    csv_generator(atm_list, city)
    return True

if __name__ == '__main__':
    get_atm_url()