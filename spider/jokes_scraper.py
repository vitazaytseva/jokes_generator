"""
Scraper implementation
"""
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from spider_settings import HEADERS, START_URLS


class JokesSpider:
    """
    Spider for scraping anecdotes from https://humornet.ru/anekdot/
    """

    def __init__(self):
        self.urls = []
        self.texts = []

    def get_links(self):
        """
        Getting all links
        """
        for link in tqdm(START_URLS):
            self.urls.append(link)
            bs_page = fetch_page(link)
            next_page = bs_page.select_one("span.page_next a")
            while next_page:
                self.urls.append(next_page.get("href"))
                bs_page = fetch_page(next_page.get("href"))
                next_page = bs_page.select_one("span.page_next a")

    def parse(self):
        """
        Parsing links
        """
        self.get_links()
        for url in tqdm(self.urls):
            response_bs = fetch_page(url)
            jokes = response_bs.select("article.block.story.shortstory")
            for joke in jokes:
                tag = re.search(r"(?<=humornet.ru/anekdot/)[\w-]+", url).group()
                text = " ".join([section.text for section in joke.select("div.text")])
                if text:
                    self.texts.append({"tag": tag, "text": text})
        return self.texts

    def _turn_to_tabular(self):
        """
        Turning texts to tabular format
        """
        data = pd.DataFrame(self.texts)
        return data

    def write_data(self):
        """
        Saving data in anecdotes_dataset.csv
        """
        data = self._turn_to_tabular()
        data.to_csv("anecdotes_dataset.csv")


def fetch_page(url):
    """
    Getting the soup
    """
    response = requests.get(url, headers=HEADERS,timeout=15).text
    soup = BeautifulSoup(response, features="lxml")
    return soup


if __name__ == "__main__":
    spider = JokesSpider()
    spider.parse()
    spider.write_data()
