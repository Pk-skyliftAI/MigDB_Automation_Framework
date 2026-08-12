from playwright.sync_api import expect

from config.settings import config
from pages.base_page import BasePage
from locators.login_locators import LoginLocators


class LoginPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_login_page(self):
        self.open(config.urls["base_url"])

    def enter_username(self, username):
        self.page.get_by_role(
            LoginLocators.USERNAME[0],
            name=LoginLocators.USERNAME[1]
        ).fill(username)

    def enter_password(self, password):
        self.page.get_by_role(
            LoginLocators.PASSWORD[0],
            name=LoginLocators.PASSWORD[1]
        ).fill(password)

    def click_sign_in(self):
        self.page.get_by_role(
            LoginLocators.SIGN_IN[0],
            name=LoginLocators.SIGN_IN[1]
        ).click()

    def login(self, username=None, password=None):

        if username is None:
            username = config.credentials["username"]

        if password is None:
            password = config.credentials["password"]

        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()

        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(3000)

    def verify_login_success(self):

        # A "Refreshing Secure Vault" dialog can cover the whole app
        # right after login with no fixed duration - confirmed live
        # 2026-08-10 this now regularly exceeds the default 5s timeout
        # (same class of race as Setup's other "Fetching.../Refreshing..."
        # dialogs elsewhere in the app).
        expect(
            self.page.get_by_role(
                "button",
                name="ORACLE admin"
            )
        ).to_be_visible(timeout=20000)

        return True

    def login_expecting_failure(self, username, password):

        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()

    def is_login_error_displayed(self):

        expect(
            self.page.get_by_role(
                LoginLocators.LOGIN_ERROR_TITLE[0],
                name=LoginLocators.LOGIN_ERROR_TITLE[1]
            )
        ).to_be_visible()

        expect(
            self.page.get_by_text(
                LoginLocators.LOGIN_ERROR_MESSAGE,
                exact=True
            )
        ).to_be_visible()

        return True

    def close_login_error(self):

        self.page.get_by_role(
            LoginLocators.OK_BUTTON[0],
            name=LoginLocators.OK_BUTTON[1]
        ).click()