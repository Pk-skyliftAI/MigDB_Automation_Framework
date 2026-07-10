from pages.google_page import GooglePage


def test_google_title(page):

    google = GooglePage(page)

    google.open()

    assert "Google" in google.title()