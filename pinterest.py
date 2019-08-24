from bs4 import BeautifulSoup as soup
from requests import get
import re
import json
import os
from tqdm import tqdm


searched_url = []  # list of first few urls fetched from google search
json_data_list = [] # list of json data fetched from pinterest url
url_list = [] # list of urls of image fetched from json

# ---------------------------------------- GET GOOGLE RESULTS ---------------------------------
def get_few_search_results(body):
    html = soup(body, 'html.parser')
    links = html.select('#main > div > div > div > a')
    print('[+] saving results ...')

    for link in links:
        link = link.get('href')
        link = re.sub(r'/url\?q=', '', link)
        searched_url.append(link)

# -------------------------- save json data from source code of given pinterest url -------------
def get_source(url):
    res = get(url)
    html = soup(res.text,'html.parser')
    # get json data from script tag having id initial-state
    json_data = html.find_all("script", attrs={"id": "initial-state"})
    for a in json_data:
        json_data_list.append(a.text)

# --------------------------- READ JSON OF PINTEREST WEBSITE ----------------------
def save_image_url():
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
        except Exception as e:
            pass

# -------------------------- get user keyword and search for that keywords ---------------------
def init():
    try:
        keyword = input("Enter keyword: ")
        keyword = keyword + " pinterest"
        keyword = keyword.replace("+", "%20")
        url = 'http://www.google.co.in/search?hl=en&q=' + keyword
        print('[+] starting search ...')
        res = get(url)
        get_few_search_results(res.content)
        buffer.close()
    except Exception as e:
        pass

# ------------------------------  download images from image url list ---------------------------
def download():
    folder_name = input("Enter folder name: ")
    for img in tqdm(url_list):
        result = get(img, stream=True).content
        filename = img.split("/")[-1]
        try:
            os.mkdir(os.path.abspath('.') + os.sep + folder_name)
        except Exception as e:
            pass
        # print(f"[+] Downloading {filename}")
        filepath = os.path.abspath('.') + os.sep + folder_name + os.sep + filename
        with open(filepath,'wb') as handler:
            handler.write(result)
        os.system("cls")
        print("")
        print("---------------- press CTRL + C to stop downloading -------------")
        print("")

# ------------------------------------- STARTING HERE -------------------------------------------

if __name__ == "__main__":
    # start intialization for search
    init()

    # get all url from google search and get source code one by one using get_source method
    print('[+] saving json data ...')
    for i in searched_url:
        get_source(i)

    # get all urls of images and save in a list
    save_image_url()

    # download images from saved images url
    print(f"[+] Total {len(url_list)} files available to download.")
    os.system("pause")
    if len(url_list):
        download()
        print("Downloading completed !!")
    else:
        print("Nothing to download !!")

    os.system("cls")
    os.system("pause")
