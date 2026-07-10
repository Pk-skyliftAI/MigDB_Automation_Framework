class BasePage:

    def __init__(self, page):
        self.page = page

    def open(self, url):
        self.page.goto(url)

    def click(self, locator):
        self.page.click(locator)

    def fill(self, locator, text):
        self.page.fill(locator, text)

    def get_text(self, locator):
        return self.page.locator(locator).text_content()

    def is_visible(self, locator):
        return self.page.locator(locator).is_visible()

    def get_title(self):
        return self.page.title()

    def get_url(self):
        return self.page.url

    def hover(self, locator):
        self.page.hover(locator)

    def press(self, locator, key):
        self.page.press(locator, key)

    def check(self, locator):
        self.page.check(locator)

    def uncheck(self, locator):
        self.page.uncheck(locator)

    def select_option(self, locator, value):
        self.page.select_option(locator, value)

    def wait_for_element(self, locator):
        self.page.wait_for_selector(locator)

    def screenshot(self, path):
        self.page.screenshot(path=path)