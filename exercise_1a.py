from bs4 import BeautifulSoup
import requests
import os
import csv

def scrape_n_store():
    ##  Checks for the file and size, if present and size > 0, uses it --- try clause
    try:
        flag = False
        if os.path.getsize('./NGO/ngo_details.html') > 0:
            with open('./NGO/ngo_details.html', 'r') as saved_file:
                soup = BeautifulSoup(saved_file, 'lxml')
                flag = True
    ##  If there's no file or file permission error -- except clause 
    except OSError as e:
        print("File Size is Zero or File not present or Permission Error")
    ## Creates and closes the file descriptor --- To store the copy for log purpose
    finally:
        if not flag:
            html_page = requests.get('https://ngodarpan.gov.in/index.php/home/sectorwise_ngo/10779/39/1?per_page=100').text
            filename = './NGO/ngo_details.html'
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            saved_file = open(filename, 'w')
            saved_file.write(html_page)
            soup = BeautifulSoup(html_page, 'lxml')
        saved_file.close()

    ## Gets the rows from the table body
    table_row_tag = soup.find('table', class_='table table-striped table-bordered table-hover Tax').find('tbody').find_all('tr')

    ngo_details = {}
    ## for loop to fetch data from each row
    for key, ngo in enumerate(table_row_tag, 1):
        details = {}
        details['Name'] = '{}'.format(ngo.find('a').text.strip().replace('\t', ''))
        details['Registration Number'] = '{}'.format(ngo.find_all('td')[2].text.split(',')[0].strip().replace('\t\n\s', ''))
        details['City'] = city = '{}'.format(ngo.find_all('td')[2].text.split(',')[1].strip().replace('\t', ''))
        details['State'] = '{}'.format(city[city.find("(")+1:city.find(")")])
        details['Address'] = ngo.find_all('td')[3].text
        details['Sectors Working In'] = ngo.find_all('td')[4].text
        ngo_details.update({key:details})
        
    ## Output to a csv file
    with open('./NGO/ngo_details.csv', 'w', newline='\n') as ngo_file:
        fieldnames = ['Name', 'Registration Number', 'City', 'State', 'Address', 'Sectors Working In']
        ngo_writer = csv.DictWriter(ngo_file, delimiter=',',fieldnames=fieldnames)
        ngo_writer.writeheader()
        for values in ngo_details.values():
            ngo_writer.writerow(values)
        
if __name__ ==  "__main__":
    scrape_n_store()