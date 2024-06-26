from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import TimeoutException
from timeit import default_timer as timer
from typing import Union
from math import ceil
import logging
import time
import os
import random
import unittest
from collections import defaultdict

logger = logging.getLogger(__name__)

class dddbCraigslist():
    def __init__(self, email:str, password:str, options: Union[FirefoxOptions, None] = None):
        if options is None:
            options = FirefoxOptions()
        
        self.email = email
        self.password = password
        self.driver = webdriver.Firefox(options=options)
        self.zip = "89436"
        self.last_time = time.time()
        self.message_size = 29998
        self.max_size = self.message_size * 20
    def login(self):
        self.driver.get("https://reno.craigslist.org")
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "cl-goto-account"))
        ).click()
        
        WebDriverWait(self.driver, 5)
        if (self.driver.current_url != "https://accounts.craigslist.org/login/home"):
            WebDriverWait(self.driver, 5).until(
                    expected_conditions.presence_of_element_located((By.ID, "inputEmailHandle"))
            ).send_keys(self.email)
            WebDriverWait(self.driver, 5).until(
                    expected_conditions.presence_of_element_located((By.ID, "inputPassword"))
            ).send_keys(self.password)
            WebDriverWait(self.driver, 5).until(
                    expected_conditions.presence_of_element_located((By.ID, "login"))
            ).click()
            self.driver.get("https://reno.craigslist.org")
            WebDriverWait(self.driver, 5).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "cl-goto-account"))
            ).click()
            if (self.driver.current_url != "https://accounts.craigslist.org/login/home"):
                self.login()

    def post(self, data:bytes, id:str="1/1", currenttime=time.time()):
        data=data.hex()
        if (len(data) > self.max_size):
            raise ValueError("too much data")
        if (len(data) > self.message_size):
            chunks = ceil(len(data)/self.message_size)
            for i in range(chunks):
                lower = i*self.message_size
                upper = lower + self.message_size
                self.post(bytes.fromhex(data[lower:upper]), "{}/{}".format(i+1,chunks), currenttime)
            return

        self.driver.get("https://reno.craigslist.org")
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.ID, "post"))
        ).click()
        # If the account has *ever* published a listing, Craigslist may ask the user
        # if they want to reuse the same data as before. This sets it to not
        # reuse the post information.
        try:
            WebDriverWait(self.driver, 2).until(
                    expected_conditions.presence_of_element_located((By.NAME, "brand_new_post"))
            ).click()
            WebDriverWait(self.driver, 2).until(
                    expected_conditions.presence_of_element_located((By.NAME, "go"))
            ).click()
        except TimeoutException:
            pass
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "(//span[@class='right-side'])[6]"))
        ).click()
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "(//span[@class='option-label'])[1]"))
        ).click()
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.ID, "PostingTitle"))
        ).send_keys(str(currenttime) + "-" + id)
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.ID, "postal_code"))
        ).send_keys(self.zip)
        el = WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.ID, "PostingBody"))
        )
        self.driver.execute_script("arguments[0].value='"+data+"';", el)
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.NAME, "go"))
        ).click()
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "continue"))
        ).click()
        # Craigslist will occasionally warn that a phone number is present in 
        # arbitrary hex data. If a "continue" button is present on the third page,
        # we are most likely on the location selection page and not the "finish 
        # draft" page.
        try:
            WebDriverWait(self.driver, 2).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "continue"))
            ).click()
            logger.info("Clicked through phone number warning")
        except TimeoutException:
            pass
        WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "done"))
        ).click()
    def get(self):
        self.driver.get("https://accounts.craigslist.org/login/home?show_tab=drafts")
        els = WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_all_elements_located((By.XPATH, "//tbody//tr/td[2]"))
        )
        table = dict()
        for el in els:
            label = el.text.split("-")
            if label[0] == '[No Title]' or float(label[0]) >= self.last_time:
                logger.debug(f"Ignoring {label} ({self.last_time=})")
                continue
            label = [float(label[0]), [int(i) for i in label[1].split("/")]]
            if label[0] not in table:
                table[label[0]]={}
            table[label[0]]["count"] = label[1][1]
            if label[1][0] not in table[label[0]]:
                table[label[0]][label[1][0]] = {}
            table[label[0]][label[1][0]]["link"] = el.find_element(By.TAG_NAME, "a").get_attribute("href")

        for _,m in table.items():
            m["content"]=""
            for i in range(1, m["count"]+1):
                if i in m:
                    self.driver.get(m[i]["link"])
                    m["content"] += WebDriverWait(self.driver, 5).until(
                            expected_conditions.presence_of_element_located((By.ID, "postingbody"))
                    ).text
                else:
                    m.pop("content")
                    break
        output = []
        for _,m in table.items():
            if "content" in m:
                output.append(bytes.fromhex(m["content"]))
        self.last_time = time.time()
        return output
        
    def close(self):
        self.driver.quit()
class TestDddbCraigslist(unittest.TestCase):
    def test_cl(self):
        with open(os.path.dirname(os.path.realpath(__file__))+"/bee-movie.txt","rb") as f:
            string = f.read()
        
        options = FirefoxOptions()    
        # options.add_argument("--headless")
        cl = dddbCraigslist(email="unrdeaddroptest@gmail.com", password="", options=options)
        cl.login()
        start=timer()
        cl.post(string)
        print(str((timer()-start)/len(string))+" Bytes/Second upload")
        start=timer()
        messages = cl.get()
        print(str((timer()-start)/len(string))+" Bytes/Second download")
        assert messages[0] == string
        cl.close()


if __name__ == "__main__":
    unittest.main()
