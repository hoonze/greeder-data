from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen, urlretrieve
import googletrans
import time
from pathlib import Path


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        keyword = self.request.query_params.get('keyword', '')

        if not keyword:
            return qs
        eng_keyword = googletrans.Translator().translate(keyword, dest='en').text.lower()
        qs = qs.filter(keyword=eng_keyword)

        # keyword에 해당하는 이미지가 없을경우 크롤링 후 DB에 저장
        if len(qs) == 0:
            crawler = Crawler()
            img_urls, img_desc = crawler.crawling(eng_keyword)
            for i in range(len(img_urls)):
                Image.objects.create(keyword=eng_keyword,
                                     desc=img_desc[i], url=img_urls[i])
            qs = qs.filter(keyword=eng_keyword)
        return qs


class Crawler():
    def __init__(self) -> None:
        pass

    def image_crawling(self, keyword):
        driver = self.driver_init()
        # 한글 -> 영어 번역

        url = 'https://unsplash.com/s/photos/' + keyword
        # 페이지 로드를 위해 3초 대기
        driver.implicitly_wait(10)
        driver.get(url)

        elem = driver.find_element_by_tag_name("body")
        for i in range(5):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)

        images = driver.find_elements_by_class_name("oCCRx")
        n = 1
        img_descs = []
        img_save_urls = []
        for image in images:
            img_urls = image.get_attribute('srcset')
            img_desc = image.get_attribute('alt')

            if img_urls is None:
                continue

            img_urls = img_urls.split()

            if len(img_urls) < 1:
                continue

            img_url = img_urls[20]
            img_descs.append(img_desc)

            self.img_resize(img_url, keyword, n)
            # with urlopen(img_url) as f:
            #     # 이미지 + 사진번호 .jpg
            #     with open('C:/SSAFY/semester2/특화PJT/image/' + keyword + str(n) + '.jpg', 'wb') as h:
            #         img = f.read()  # 이미지 읽기
            #         h.write(img)
            # DB저장용 url
            img_save_urls.append(keyword+str(n))
            n += 1
            if n > 20:
                break
        driver.close()
        return img_save_urls, img_descs

    def img_resize(self, img_url, keyword, n):
        from PIL import Image, ImageOps
        f = urlretrieve(img_url, "test.jpg")
        im = Image.open("test.jpg")
        # Target size parameters
        width = 1920
        height = 1080

        # Resize input image while keeping aspect ratio
        ratio = height / im.height
        im = im.resize((int(im.width * ratio), height))

        # Border parameters
        fill_color = (0, 0, 0)
        border_l = int((width - im.width) / 2)

        # Approach #1: Use ImageOps.expand()
        border_r = width - im.width - border_l
        im_1 = ImageOps.expand(im, (border_l, 0, border_r, 0), fill_color)
        im_1.save('/home/ubuntu/images/keywords/' + keyword + str(n) + '.jpg')

    def driver_init(self):
        # options = webdriver.ChromeOptions()
        # options.add_experimental_option("detach", True)
        # driver = webdriver.Chrome(
        #     chrome_options=options,  executable_path=r'C:/SSAFY/semester2/특화PJT/greeder-data/chromedriver.exe')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(chrome_options=chrome_options)

        return driver

    def crawling(self, keyword):
        return self.image_crawling(keyword)
