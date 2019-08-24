# pinterest-image-scrap
This python (3.7) program scrap data from pinterest without official API.

>NOTE: It will definetly take more memory (according to the size of images) to download it.

### install all required libraries using following command from your project directory     
``` pip install -r requirements.txt ```

## HOW IT SCRAP?
```
 -> it uses google search using python curl to get some results and then visit every page in results
 -> it scrap json data from pinterest page and get image urls
 -> download each and every image from url list and save it on hard disk
 
 ```
