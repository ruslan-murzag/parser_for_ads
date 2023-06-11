import time
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd



class AdParser:
    def __init__(self, url, paginator, ads, contents, driver_url, closer, login=None, password=None, host=None, db=None, table_name=None):
        self.url = url
        self.paginator = paginator
        self.contents = contents
        self.driver_url = driver_url
        self.ads = ads
        self.closer = closer

        self.host = host
        self.login = login
        self.password = password
        self.db = db
        self.table_name = table_name
        try:
            service = Service(executable_path=self.driver_url)
            self.driver = webdriver.Chrome(service=service)
        except Exception as ex:
            print('Driver url error')
            print(ex)

    #show data in pandas
    def get_content(self):
        try:
            self.driver.maximize_window()
            self.driver.get(self.url)
            pagination = self.driver.find_elements(By.CLASS_NAME, self.paginator)
            res = []
            for page in range(0, 5):
                ads = self.driver.find_elements(By.CLASS_NAME, self.ads)
                for ad in range(0, len(ads)):

                    self.driver.find_elements(By.CLASS_NAME, self.ads)[ad].click()
                    ads_list = []

                    for content in self.contents:
                        ads_list.append(self.driver.find_element(By.CLASS_NAME, content).text)

                    ads_list.append(self.driver.current_url)
                    print(self.driver.current_url)
                    print(ads_list)
                    self.driver.find_element(By.CLASS_NAME, self.closer).click()
                    res.append(ads_list)
                    ads_list = []
                    time.sleep(0.5)
                time.sleep(2)
                self.driver.find_elements(By.CLASS_NAME, self.paginator)[page + 1].click()

            df = pd.DataFrame(res, columns=['title', 'description', 'url'])
            return df

        except Exception as ex:
            print(ex)

    #from pandas add data to postgres sql
    def to_db(self):
        engine = create_engine(f'postgresql://{self.login}:{self.password}@{self.host}/{self.db}')
        df = self.get_content()
        df.to_sql(self.table_name, engine)
        return 'Everything good!'

astana_hub = AdParser(url="https://astanahub.com/ru/vacancy/", paginator='paginator', ads='tiny-content',
                      contents=['block-title', 'vacancy-content'], driver_url='chromedriver_mac_arm64/chromedriver',
                      closer='back-btn', db='Astana_hub_vac', login='Parser', password='admin',
                      table_name='astana_hub_vac', host='localhost:5432' )

print(astana_hub.to_db())