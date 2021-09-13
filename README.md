# pinterest-image-scrap
[![built with Python](https://img.shields.io/badge/Made%20with-Python3-red?style=for-the-badge&logo=python)](https://www.python.org/)
[![built with BeautifulSoup](https://img.shields.io/badge/Made%20with-BeautifulSoup-blue?style=for-the-badge&logo=bs4)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

This python3 program scrap data from pinterest without official API.

>NOTE: It will definetly take some memory (depends on the size of images) to download it.

### install all required libraries using following command from your project directory     
``` pip install -r requirements.txt ```

### how to run

1) directly
```python pinterest.py```

2) using import
```
from pinterest import PinterestImageScraper
p_scraper = PinterestImageScraper()
is_downloaded = p_scraper.make_ready("messi")
```
