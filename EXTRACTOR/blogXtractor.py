from bs4 import BeautifulSoup
from selenium import webdriver
import time

url = 'https://en.wordpress.com/tag/music/'

driver = webdriver.Chrome("./chromedriver")

driver.get(url)
data = driver.page_source

soup = BeautifulSoup(data, "html.parser")

links_list = soup.find_all('a', class_="blog-url")
print(links_list)

time.sleep(12)

for single_link in links_list:
    link = single_link['href']
    print(link)
