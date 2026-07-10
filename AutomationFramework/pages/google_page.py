from pages.base_page import BasePage
from locators.google_locators import GoogleLocators


class GooglePage(BasePage):

    URL = "https://www.google.com"

    def __init__(self, page):
        super().__init__(page)

    def open(self):
        super().open(self.URL)

    def search(self, text):
        self.fill(GoogleLocators.SEARCH_BOX, text)
        self.page.keyboard.press("Enter")

    def title(self):
        return self.get_title()