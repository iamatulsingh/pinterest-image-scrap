import json
import os
import cv2
import numpy as np

from requests import get
from tqdm import tqdm
from bs4 import BeautifulSoup as soup
from concurrent.futures import ThreadPoolExecutor

from pydotmap import DotMap


class PinterestImageScraper:

    def __init__(self):
        self.json_data_list = []
        self.unique_img = []

    @staticmethod
    def clear():
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')

    # ---------------------------------------- GET GOOGLE RESULTS ---------------------------------
    @staticmethod
    def get_pinterest_links(body, max_images: int):
        searched_urls = []
        html = soup(body, 'html.parser')
        links = html.select('#b_results cite')
        for link in links:
            link = link.text
            if "pinterest" in link:
                searched_urls.append(link)
                # stops adding links if the limit has been reached
                if max_images is not None and max_images == len(searched_urls):
                    break
        return searched_urls

    # -------------------------- save json data from source code of given pinterest url -------------
    def get_source(self, url: str, proxies: dict) -> None:
        try:
            res = get(url, proxies=proxies)
        except Exception:
            return
        html = soup(res.text, 'html.parser')
        json_data = html.find_all("script", attrs={"id": "__PWS_INITIAL_PROPS__"})
        self.json_data_list.append(json.loads(json_data[0].string))

    # --------------------------- READ JSON OF PINTEREST WEBSITE ----------------------
    def save_image_url(self, max_images: int) -> list:
        url_list = []
        for js in self.json_data_list:
            try:
                data = DotMap(js)
                urls = []
                for pin in data.initialReduxState.pins:
                    if isinstance(data.initialReduxState.pins[pin].images.get("orig"), list):
                        for i in data.initialReduxState.pins[pin].images.get("orig"):
                            urls.append(i.get("url"))
                    else:
                        urls.append(data.initialReduxState.pins[pin].images.get("orig").get("url"))

                for url in urls:
                    url_list.append(url)
                    if max_images is not None and max_images == len(url_list):
                        return list(set(url_list))
            except Exception:
                continue

        return list(set(url_list))

    # ------------------------------ image hash calculation -------------------------
    def dhash(self, image, hashSize=8):
        resized = cv2.resize(image, (hashSize + 1, hashSize))
        diff = resized[:, 1:] > resized[:, :-1]
        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

    # ------------------------------  save all downloaded images to folder ---------------------------
    def saving_op(self, var):
        url_list, folder_name = var
        if not os.path.exists(os.path.join(os.getcwd(), folder_name)):
            os.mkdir(os.path.join(os.getcwd(), folder_name))
        for img in tqdm(url_list):
            result = get(img, stream=True).content
            file_name = img.split("/")[-1]
            file_path = os.path.join(os.getcwd(), folder_name, file_name)
            img_arr = np.asarray(bytearray(result), dtype="uint8")
            image = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            if not self.dhash(image) in self.unique_img:
                cv2.imwrite(file_path, image)
            self.unique_img.append(self.dhash(image))
            print("", end="\r")

    # ------------------------------  download images from image url list ----------------------------
    def download(self, url_list, keyword):
        folder_name = keyword
        num_of_workers = 10
        idx = len(url_list) // num_of_workers if len(url_list) > 9 else len(url_list)
        param = []
        for i in range(num_of_workers):
            param.append((url_list[((i*idx)):(idx*(i+1))], folder_name))
        with ThreadPoolExecutor(max_workers=num_of_workers) as executor:
            executor.map(self.saving_op, param)
        PinterestImageScraper.clear()

    # -------------------------- get user keyword and google search for that keywords ---------------------
    @staticmethod
    def start_scraping(max_images, key=None, proxies={}):
        assert key is not None, "Please provide keyword for searching images"
        keyword = key + " pinterest"
        keyword = keyword.replace("+", "%20")
        url = f'https://www.bing.com/search?q={keyword}&pq=messi+pinterest&first=1&FORM=PERE'
        res = get(url, proxies=proxies)
        searched_urls = PinterestImageScraper.get_pinterest_links(res.content, max_images)

        return searched_urls, key.replace(" ", "_")

    def make_ready(self, key=None):
        extracted_urls, keyword = PinterestImageScraper.start_scraping(max_images=None, key=key)

        self.json_data_list = []
        self.unique_img = []

        print('[+] saving json data ...')
        for i in extracted_urls:
            self.get_source(i, {})

        # get all urls of images and save in a list
        url_list = self.save_image_url(max_images=None)

        # download images from saved images url
        print(f"[+] Total {len(url_list)} files available to download.")
        print()

        if len(url_list):
            try:
                self.download(url_list, keyword)
            except KeyboardInterrupt:
                return False
            return True

        return False


if __name__ == "__main__":
    p_scraper = PinterestImageScraper()
    is_downloaded = p_scraper.make_ready("messi")

    if is_downloaded:
        print("\nDownloading completed !!")
    else:
        print("\nNothing to download !!")
