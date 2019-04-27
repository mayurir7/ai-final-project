import requests
from bs4 import BeautifulSoup
page = requests.get("https://www.wunderground.com/history/daily/KSFO/date/2018-4-17?req_city=San%20Francisco&req_state=CA&req_statename=California&reqdb.zip=94102&reqdb.magic=1&reqdb.wmo=99999")

print(page)
print(page.content)
print(" ")
soup = BeautifulSoup(page.content, "html.parser")
#print("SOUP:")
#print(soup)
#print("ENDSOUP")
#li = soup.find_all("div")
#print(li)
