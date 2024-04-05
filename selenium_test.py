from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
# import re

DELAY = 5
URL = "https://habr.com/ru/search/?q=pgpool&target_type=posts&order=relevance"
MAX_LOAD_MORE_CLICKS = 5

driver = webdriver.Chrome()
driver.get(URL)

reviews_lst = []
urls_lst = []
dates_lst = []

try:
    list_articles_link = driver.find_elements(
        By.XPATH, "//*[@class='tm-article-snippet__readmore']"
    )
    for link in list_articles_link:
        # Вырежем пустые оценки по критериям
        text = link.get_attribute("href")
        reviews_lst.append({"href": text})
except TimeoutException:
    pass

print(reviews_lst)

# scrapedReviews = pd.DataFrame(reviews)
# scrapedReviews.insert(0, "id", range(0, 0 + len(scrapedReviews)))
# scrapedReviews.to_csv("scrapedReviews.csv", index=False)
