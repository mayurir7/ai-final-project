import requests
from selenium import webdriver
import os
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import sys

def getData2(dateString):
    for i in range(10):
        try:
            print(getData(dateString)),
            break
        except Exception as ex:
            sys.stderr.write("Exception " + str(ex) + "\n")
def getData(dateString):
    ret = ""
    driver = webdriver.PhantomJS("../lib/phantomjs/bin/phantomjs")
    driver.get("https://www.wunderground.com/history/daily/us/ca/san-francisco/KSFO/date/" + dateString)
    time.sleep(15)
    history = driver.find_element_by_id("history-observation-table")
    rows = history.find_elements_by_tag_name("tr")
    i = 0
    lasthour = 0
    isPM = True
    for row in rows:
        i = i + 1
        if(i == 1):
            continue
        cols = row.find_elements_by_tag_name("td")
        timeD = cols[0]
        temp = cols[1]
        windspeed = cols[5]
        cond = cols[10]
        data = [timeD.find_element_by_tag_name("span").get_attribute('innerHTML').encode('utf-8'), temp.find_element_by_tag_name("span").find_element_by_tag_name("span").get_attribute('innerHTML').encode('utf-8'), windspeed.find_element_by_tag_name("span").find_element_by_tag_name("span").get_attribute('innerHTML').encode('utf-8'), cond.find_element_by_tag_name("span").get_attribute('innerHTML').encode('utf-8')]
        timeData = data[0].split(" ")
        hour, minute = timeData[0].split(":")
        hour = (int(hour) + 10) % 12
        if(hour == 0 and lasthour != 0):
            isPM = not isPM
        lasthour = hour
        hour = hour + (12 if isPM else 0)
        data[0] = str(hour) + ":" + minute
        ret = ret + (",\t".join(data)) + "\n"
    try:
        driver.quit()
    except:
        pass
    return ret

daysPerMonth = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#for year in range(2017, 2019):
#    for month in range(1, 13):
#        for day in range(1, daysPerMonth[month] + 1):
#            getData(str(year) + "-" + str(month) + "-" + str(day))

year = 2017
for month in range(12, 13):
    for day in range(1, daysPerMonth[month] + 1):
        getData2(str(year) + "-" + str(month) + "-" + str(day))
        sys.stderr.write("Month " + str(month) + " Day: " + str(day) + "\n")
