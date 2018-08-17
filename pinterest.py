from bs4 import BeautifulSoup as soup
from requests import get
import re
import pycurl
from io import BytesIO
import json
import urllib
import os
import time
from tqdm import tqdm


searched_url = []  # list of first few urls fetched from google search
json_data_list = [] # list of json data fetched from pinterest url
url_list = [] # list of urls of image fetched from json

# ---------------------------------------- GET GOOGLE RESULTS ---------------------------------

def get_few_search_results(body):
    html = soup(body,'html.parser')
    links = html.select('.r')
    print('[+] saving results ...')
    for link in links:
        #link.findAll('a',attrs={'href': re.compile("^http://")})
        for a in link:
            s = a.get('href')
            searched_url.append(s[7:])
            # s[7:] remove "/url?q=" from starting of the result string of google search


# -------------------------- save json data from source code of given pinterest url -------------
def get_source(url):
    res = get(url)
    html = soup(res.text,'html.parser')
    json_data = html.find_all("script", attrs={"id":"initial-state"}) #get json data from script tag having id initial-state
    for a in json_data:
        json_data_list.append(a.text)

# --------------------------- READ JSON OF PINTEREST WEBSITE ----------------------

def save_image_url():
    # with open('document.json') as f:
    #     data = json.load(f)

    print('[+] saving image urls ...')
    for js in json_data_list:
        try:
            data = json.loads(js)
            dct = data['resources']['data']['ReactBoardFeedResource']
            for key in dct.keys():
                dct_length = len(data['resources']['data']['ReactBoardFeedResource'][key]['data']['board_feed'])
                for i in range(dct_length):
                    img = data['resources']['data']['ReactBoardFeedResource'][key]['data']['board_feed'][i]['images']['orig']['url']
                    url_list.append(img)
        except Exception:
            print("")


# -------------------------- get user keyword and search for that keywords ---------------------
def init():
    try:
        keyword = input("Enter keyword: ")
        keyword = keyword + " pinterest"
        keyword = keyword.replace(" ", "%20")
        url = 'http://www.google.co.in/search?hl=en&q=' + keyword
        print('[+] starting search ...')
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write) # writing data (html source code) to buffer
        c.perform()
        # with open('o.html', 'wb') as f:
        #     c.setopt(c.WRITEFUNCTION, f.write)
        #     c.perform()

        get_few_search_results(buffer.getvalue())
        buffer.close()
    except Exception:
        print("")


# ------------------------------  download images from image url list ---------------------------
def download():
    folder_name = input("Enter folder name: ")
    for img in tqdm(url_list):
        result = get(img,stream=True).content
        filename = img.split("/")[-1]
        try:
            os.mkdir(os.path.abspath('.')+os.sep+folder_name)
        except Exception:
            pass
        #print("[+] Downloading %s" % filename)
        filepath = os.path.abspath('.')+os.sep+folder_name+os.sep+filename
        with open(filepath,'wb') as handler:
            handler.write(result)
        os.system("cls")
        print("")
        print("---------------- press CTRL + C to stop downloading -------------")
        print("")

# ------------------------------------- STARTING HERE -------------------------------------------

# start intialization for search
init()

# get all url from google search and get source code one by one using get_source method
print('[+] saving json data ...')
for i in searched_url:
    get_source(i)

# get all urls of images and save in a list
save_image_url()

# download images from saved images url
print("[+] Total %s " % len(url_list) + " files available to download.")
os.system("pause")
#progressbar = tqdm(total=len(url_list))
download()

os.system("cls")
print("downloading completed !!")
os.system("pause")

