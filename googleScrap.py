import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openpyxl
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
import sys
import csv
# from selenium.webdriver.support.ui import WebDriverWait

def headlessDriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--window-size=1920, 900")
    options.add_argument("--hide-scrollbars")
    try:
        driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
        agent = driver.execute_script("return navigator.userAgent")
        driver.close()
        options.add_argument("user-agent="+agent)
        driver= webdriver.Chrome(options= options, executable_path="chromedriver.exe")
        
        return driver
    except:
        print("You must use same chrome version with chrome driver!")
        return 0
        
def headDriver():
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")
    try:
        driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
        agent = driver.execute_script("return navigator.userAgent")
        driver.close()
        options.add_argument("user-agent="+agent)
        driver= webdriver.Chrome(options= options, executable_path="chromedriver.exe")
        return driver
    except:
        print("You must use same chrome version with chrome driver!")
        return 0

class GoogleScraper():
    def writeCsvheader(self, filename, columns):
        try:
            os.remove(filename)
        except:
            pass
        df= pd.DataFrame(columns= columns)
        # filename= str(datetime.datetime.now()).replace(':', '-')+'.csv'
        df.to_csv(filename, mode= 'x', index= False, encoding='utf-8-sig')
        # return filename
    def readCsv(self, filename, lineCount):
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count != lineCount:
                    line_count += 1
                    continue
                else:
                    print("row", row)
                    company_id = row['ï»¿company_id']
                    url= row['url']
                    print("url", url)
                    return {'companyId': company_id, 'url': url}
            print(f'Processed {line_count} lines.')
    def saveToCsv(self, filename, newPage, columns):
        df = pd.DataFrame(newPage, columns = columns)
        print("Now items writed in csv file!")
        df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')

    def scrape(self):
        columns = ['company_id', 'url', 'review_score',
                   'review_count', 'last_review']
        filename= "googleResult.csv"
        self.writeCsvheader(filename, columns)

        # intendedUrl= "https://www.google.com/maps/place/Fonci%C3%A8re+Magellan/@48.8757885,2.2893423,17z/data=!3m1!4b1!4m5!3m4!1s0x47e66e30133f5c05:0xb054bf1237508802!8m2!3d48.875785!4d2.291531"
        # intendedUrl = "https://www.google.com/maps/place/Candriam+-+France/@48.8741343,2.3024379,17z/data=!3m1!4b1!4m5!3m4!1s0x47e66fc11bee42d1:0x466225a248da15ab!8m2!3d48.8741316!4d2.3046312"

        # you can modify this to scrap specific part or use loop for all rows.
        rowToScrap= 1
        primaryData = self.readCsv('Google_Urls.csv', rowToScrap)
        print("primaryData", primaryData)
        intendedUrl= primaryData['url']
        company_id = primaryData['companyId']
        driver= headlessDriver()
        driver.get(intendedUrl)
        time.sleep(2)
        soup= BeautifulSoup(driver.page_source, 'html.parser')
        reviewScore= 0
        reviewCount= 0
        lastReview= 0
        try:
            reviewScore= soup.find('div', attrs= {'class': 'gm2-display-2'}).text.strip()
            reviewCount= soup.find('button', attrs= {'class': 'gm2-button-alt mapsConsumerUiSubviewSectionGm2Reviewchart__button-blue'}).text.strip()
        except:
            pass
        sortBtn = driver.find_element_by_xpath(
            "//button[@class='mapsConsumerUiSubviewSectionGm2Actionchip__button gm2-hairline-border section-action-chip-button']")
        print("reviewCount", reviewCount)
        newPage = []
        new = {'company_id': company_id, 'url': intendedUrl, 'review_score': reviewScore,
               'review_count': reviewCount, 'last_review': lastReview}
        newPage.append(new)
        self.saveToCsv(filename, newPage, columns)

if __name__ == '__main__':
    scraper = GoogleScraper()
    scraper.scrape()
