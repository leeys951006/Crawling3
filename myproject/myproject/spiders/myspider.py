import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://nodejs.org/en']  # 크롤링할 웹사이트의 URL

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 브라우저 창을 표시하지 않으려면 주석 해제
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # 10초 대기 설정

    def start_requests(self):
        for url in self.start_urls:
            self.driver.get(url)
            try:
                # 예를 들어, 특정 요소가 로드될 때까지 대기
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
            except Exception as e:
                self.logger.error(f"Error waiting for page load: {e}")
            html = self.driver.page_source
            yield scrapy.Request(url, callback=self.parse, meta={'html': html})

    def parse(self, response):
        # HTML을 meta에서 가져오기
        html = response.meta['html']
        response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        # 타이틀 추출
        titles = response.css('h1::text').getall()
        self.logger.info(f"Titles found: {titles}")

        # 본문 내용 추출 (예시: p 태그)
        paragraphs = response.css('p::text').getall()
        self.logger.info(f"Paragraphs found: {paragraphs}")

        # 링크 추출 (예시: a 태그의 href 속성)
        links = response.css('a::attr(href)').getall()
        self.logger.info(f"Links found: {links}")

        # 추출한 데이터를 yield
        for title in titles:
            yield {'title': title}
        for paragraph in paragraphs:
            yield {'paragraph': paragraph}
        for link in links:
            yield {'link': link}

    def close(self, reason):
        self.driver.quit()  # 스파이더가 종료될 때 브라우저를 종료합니다.
