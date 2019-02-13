import os
import unittest

from parameterized import parameterized
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class SearchPage:
    SEARCH_INPUT = (By.CSS_SELECTOR, 'input#text')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    LOGIN_BUTTON = (By.CSS_SELECTOR, 'a[href="https://mail.yandex.ru"]')
    YANDEX_LINK = (By.CSS_SELECTOR, 'a[href="https://mail.yandex.ru"]')
    VOICE_SEARCH = (By.CSS_SELECTOR, '.input__voice-search')

    @staticmethod
    def trait(driver):
        return "Яндекс" in driver.title


class ResultsPage:
    RESULTS_LIST = (By.CSS_SELECTOR, 'ul.serp-list')
    RESULT_TEXTS = (By.CSS_SELECTOR, ".organic__url-text")

    @staticmethod
    def trait(driver):
        return "Яндекс: нашлось" in driver.title


class SeleniumTest(unittest.TestCase):
    DEFAULT_SELENIUM_TIMEOUT = os.getenv("SELENIUM_TIMEOUT_SEC", 5)

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def page_loaded(self, page_class):
        try:
            if "trait" in page_class.__dict__ and callable(page_class.trait):
                self._wait().until(lambda driver: page_class.trait(driver))

            for name, value in page_class.__dict__.items():
                if isinstance(value, tuple):
                    self.s(value)
        except TimeoutException as te:
            msg = "Failed to validate `{}` page is open".format(page_class.__name__)
            raise RuntimeError(msg) from te

    def _wait(self):
        return WebDriverWait(self.driver, timeout=SeleniumTest.DEFAULT_SELENIUM_TIMEOUT)

    # Browsers has nice $ and $$ methods in console to search for HTML elements.
    # Lets pretend we could have them too. Though, $ and $$ aren't valid identifiers in python.
    def s(self, by_and_locator_tuple):
        try:
            return self._wait().until(lambda driver: driver.find_element(*by_and_locator_tuple))
        except TimeoutException as te:
            msg = "Can't find element `{}` in time".format(by_and_locator_tuple)
            raise RuntimeError(msg) from te

    def ss(self, by_and_locator_tuple):
        try:
            return self._wait().until(lambda driver: driver.find_elements(*by_and_locator_tuple))
        except TimeoutException as te:
            msg = "Can't find elements `{}` in time".format(by_and_locator_tuple)
            raise RuntimeError(msg) from te


# The demo task is quite short, so no actions could be extracted from it.
# In normal scenario there would be 3 parts: the locators, the actions and the scenarios in tests.
class YandexSearch(SeleniumTest):
    # N.B. Yandex will flood protect itself if too many same queries be made.
    base_url = os.getenv("BASE_URL", "https://ya.ru")

    @parameterized.expand(["Владивосток"])
    def test_search_in_yandex(self, query):
        self.driver.get(YandexSearch.base_url)
        self.page_loaded(SearchPage)

        self.s(SearchPage.SEARCH_INPUT).send_keys(query)
        self.s(SearchPage.SUBMIT_BUTTON).click()

        self.page_loaded(ResultsPage)

        # Silly check if we see correct results.
        # For other words we would need some sort of oracle to see relevance with what we're looking for.
        self.assertTrue(all([query in el.text for el in self.ss(ResultsPage.RESULT_TEXTS)]))


if __name__ == "__main__":
    unittest.main()
