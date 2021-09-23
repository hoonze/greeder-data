from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
import googletrans


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        keyword = self.request.query_params.get('keyword', '')
        eng_keyword = googletrans.Translator().translate(keyword, dest='en').text.lower()
        if eng_keyword:
            qs = qs.filter(keyword=eng_keyword)

        # keyword에 해당하는 이미지가 없을경우 크롤링 후 DB에 저장
        if len(qs) == 0:
            crawler = Crawler()
            img_urls, img_desc = crawler.crawling(eng_keyword)
            for i in range(20):
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
        driver.implicitly_wait(3)
        driver.get(url)

        elem = driver.find_element_by_tag_name("body")
        for i in range(5):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.4)

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
            temp = [img_desc]
            img_descs.append(temp)
            with urlopen(img_url) as f:
                with open('C:/SSAFY/2학기/특화PJT/특화PJT/crawler/images/' + keyword + str(n) + '.jpg', 'wb') as h:  # 이미지 + 사진번호 .jpg
                    img = f.read()  # 이미지 읽기
                    h.write(img)
            img_save_urls.append(
                'C:/SSAFY/2학기/특화PJT/특화PJT/crawler/images/' + keyword + str(n) + '.jpg')
            n += 1
            if n > 20:
                break
        print(img_save_urls)
        print(img_descs)
        return img_save_urls, img_descs

    def driver_init(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(
            chrome_options=options,  executable_path=r'C:/SSAFY/2학기/특화PJT/특화PJT/crawler/chromedriver.exe')

        return driver

    def crawling(self, keyword):
        return self.image_crawling(keyword)

    # def get(self, request):
    #     # 여러개의 객체를 serialization하기 위해 many = True로 설정
    #     return self.list(request)

    # def post(self, request):
    #     return self.create(request)
