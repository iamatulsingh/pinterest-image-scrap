import sys
import re
import json
import os

from requests import get
from bs4 import BeautifulSoup as soup
from tqdm import tqdm


class PinterestImageScraper:

    def __init__(self):
        self.json_data_list = []

    # ---------------------------------------- GET GOOGLE RESULTS ---------------------------------
    def get_pinterest_links(self, body):
        searched_urls = []
        html = soup(body, 'html.parser')
        links = html.select('#main > div > div > div > a')
        print('[+] saving results ...')

        for link in links:
            link = link.get('href')
            link = re.sub(r'/url\?q=', '', link)
            if link[0] != "/" and "pinterest" in link:
                searched_urls.append(link)

        return searched_urls


    # -------------------------- save json data from source code of given pinterest url -------------
    def get_source(self, url):
        try:
            res = get(url)
        except Exception:
            return
        html = soup(res.text,'html.parser')
        # get json data from script tag having id initial-state
        json_data = html.find_all("script", attrs={"id": "initial-state"})
        for a in json_data:
            self.json_data_list.append(a.text)


    # --------------------------- READ JSON OF PINTEREST WEBSITE ----------------------
    def save_image_url(self):
        print('[+] saving image urls ...')
        url_list = []
        for js in self.json_data_list:
            try:
                data = json.loads(js)
                dct = data['resources']['data']['ReactBoardFeedResource']
                for key in dct.keys():
                    dct_length = len(data['resources']['data']['ReactBoardFeedResource'][key]['data']['board_feed'])
                    for i in range(dct_length):
                        img = data['resources']['data']['ReactBoardFeedResource'][key]['data']['board_feed'][i]['images']['orig']['url']
                        url_list.append(img)
            except Exception:
                pass

        return url_list

    # ------------------------------  download images from image url list ---------------------------
    def download(self, url_list):
        folder_name = input("Enter folder name: ")
        for img in tqdm(url_list):
            result = get(img, stream=True).content
            filename = img.split("/")[-1]
            try:
                os.mkdir(os.path.abspath('.') + os.sep + folder_name)
            except Exception:
                pass
            filepath = os.path.abspath('.') + os.sep + folder_name + os.sep + filename
            with open(filepath,'wb') as handler:
                handler.write(result)
            if sys.platform == "win32":
                os.system("cls")
            elif sys.platform == "linux" or sys.platform == "linux2":
                os.system("clear")
            print("")
            print("---------------- press CTRL + C to stop downloading -------------")
            print("")

    # -------------------------- get user keyword and google search for that keywords ---------------------
    def start_scrape(self):
        try:
            keyword = input("Enter keyword: ")
            keyword = keyword + " pinterest"
            keyword = keyword.replace("+", "%20")
            url = 'http://www.google.co.in/search?hl=en&q=' + keyword
            print('[+] starting search ...')
            res = get(url)
            searched_urls = self.get_pinterest_links(res.content)
        except Exception as e:
            print(e)
            return []

        return searched_urls

    def make_ready(self):
        searched_url = self.start_scrape()

        print('[+] saving json data ...')
        for i in searched_url:
            self.get_source(i)

        # get all urls of images and save in a list
        url_list = self.save_image_url()

        # download images from saved images url
        print(f"[+] Total {len(url_list)} files available to download.")
        print("\nPress enter to continue ...")
        input()

        if len(url_list):
            self.download(url_list)
            return True
        else:
            return False


if __name__ == "__main__":
    p_scraper = PinterestImageScraper()
    is_downloaded = p_scraper.make_ready()

    if is_downloaded:
        print("Downloading completed !!")
    else:
        print("Nothing to download !!")
