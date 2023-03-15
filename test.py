from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import json
import requests
import pandas as pd
import io

# define a function to split a string at a certain occurance of a separator

# https://stackoverflow.com/questions/36300158/split-text-after-the-second-occurrence-of-character
def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])


chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
chrome_options.add_argument("--headless=new")


#open file with last mnt year saved in it
file = open("mth-yr.txt","r+")

driver = webdriver.Chrome(options = chrome_options)

driver.get('https://corsproxy.io/?https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindicescpiandretailpricesindexrpiitemindicesandpricequotes/data')
text= driver.find_element(By.TAG_NAME,'pre').text
data = json.loads(text)
datasets = data['datasets']

#go through the dataset and find the first one which doesn't contain the word framework, glossary or /pricequotes. The url includes pricesquotes so that slash is important. Save the index as the variable match  
for i,dataset in enumerate(datasets):
    match = i
    if('framework' not in dataset['uri'] and 'glossary' not in dataset['uri'] and '/pricequotes' not in dataset['uri']):
        break

#get the uri of the items dataset we want
items = data['datasets'][match]['uri']

#get the month and year from the uri
date=split(items,'itemindices',2)[1]

if (file.read() != date):
    with webdriver.Chrome(options= chrome_options) as driver: 
        driver.get("https://corsproxy.io/?https://www.ons.gov.uk"+items+"/data")

        itemsurl= driver.find_element(By.TAG_NAME,'pre').text
        itemspage = json.loads(itemsurl)
        csv = itemspage['downloads'][0]['file']
       
        print("https://corsproxy.io/?https://www.ons.gov.uk/file?uri="+items+"/"+csv)
    #     driver.get("https://corsproxy.io/?https://www.ons.gov.uk/file?uri="+items+"/"+csv)

    #     # closing browser
        driver.close()
    
    with requests.Session() as s:
        download = s.get("https://corsproxy.io/?https://www.ons.gov.uk/file?uri="+items+"/"+csv,headers={'User-Agent': 'Mozilla/5.0'})
        
        read=pd.read_csv(io.StringIO(download.content.decode('utf-8')))
        read.to_csv(csv)
#     file.write(date)

with open("csv.txt",'w') as file:
    file.write(csv)
