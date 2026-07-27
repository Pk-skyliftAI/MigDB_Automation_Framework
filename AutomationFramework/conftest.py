from pathlib import Path

import pytest
from config.settings import config
from utils.browser_manager import BrowserManager
from utils.logger import Logger
from utils.screenshot_manager import ScreenshotManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.navigation_page import NavigationPage
from pages.manage_page import ManagePage
from pages.monitor_page import MonitorPage
from pages.designer_page import DesignerPage
from pages.vault_page import VaultPage
from pages.setup_page import SetupPage
from pages.supplemental_logging_page import SupplementalLoggingPage
from pages.parameter_file_page import ParameterFilePage
from pages.config_tables_page import ConfigTablesPage
from pages.connections_page import ConnectionsPage
from pages.purge_cdc_files_page import PurgeCdcFilesPage
from pages.assessment_page import AssessmentPage

logger = Logger.get_logger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        choices=["chromium", "firefox", "webkit"],
        help="Browser to execute tests on."
    )

@pytest.fixture(scope="function")
def browser(request):

    browser_name = request.config.getoption("--browser")

    manager = BrowserManager(browser_name=browser_name)

    browser = manager.start_browser()

    logger.info(
        f"Browser launched successfully: {browser_name or config.browser['engine']}"
    )

    yield browser

    logger.info("Closing browser.")

    manager.stop_browser()


@pytest.fixture(scope="function")
def context(browser, request):
    record_video = config.reporting.get("video", False)

    context = browser.new_context(
        record_video_dir="reports/videos" if record_video else None
    )

    if config.reporting.get("trace", False):
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    logger.info("Browser context created.")

    yield context

    if config.reporting.get("trace", False):
        trace_path = Path("reports") / "traces" / f"{request.node.name}.zip"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        context.tracing.stop(path=str(trace_path))

    logger.info("Closing browser context.")
    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()

    # Make page available to pytest hooks
    request.node.page = page

    logger.info("New browser page created.")

    yield page

    logger.info("Closing browser page.")

    # page.video is only finalized once the page closes, so grab the
    # handle first and rename it with the test name afterward - the
    # in-progress file has a random name Playwright assigns on creation.
    video = page.video if config.reporting.get("video", False) else None

    page.close()

    if video:
        final_path = Path("reports") / "videos" / f"{request.node.name}.webm"
        Path(video.path()).rename(final_path)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.failed:
        page = getattr(item, "page", None)

        if page:
            try:
                screenshot_path = ScreenshotManager.capture(
                    page,
                    item.name
                )

                logger.error(f"Test Failed: {item.name}")
                logger.error(f"Screenshot saved: {screenshot_path}")

            except Exception as e:
                logger.exception(
                    f"Unable to capture screenshot for '{item.name}'. Error: {e}"
                )
# ----------------------------
# Login Fixtures
# ----------------------------

@pytest.fixture
def login(page):
    """Unauthenticated LoginPage object. Used by login/invalid-login tests."""
    return LoginPage(page)


@pytest.fixture
def logged_in_page(page):

    login = LoginPage(page)

    login.open_login_page()

    login.login()

    return page              

# ----------------------------
# Page Fixtures
# ----------------------------

@pytest.fixture
def dashboard(logged_in_page):
    return DashboardPage(logged_in_page)


@pytest.fixture
def navigation(logged_in_page):
    return NavigationPage(logged_in_page)


@pytest.fixture
def manage(logged_in_page):
    return ManagePage(logged_in_page)


@pytest.fixture
def monitor(logged_in_page):
    return MonitorPage(logged_in_page)


@pytest.fixture
def designer(logged_in_page):
    return DesignerPage(logged_in_page)  

@pytest.fixture
def vault(logged_in_page):
    return VaultPage(logged_in_page)

@pytest.fixture
def setup(logged_in_page):
    return SetupPage(logged_in_page)

@pytest.fixture
def supplemental_logging(logged_in_page):
    return SupplementalLoggingPage(logged_in_page)

@pytest.fixture
def parameter_file(logged_in_page):
    return ParameterFilePage(logged_in_page)

@pytest.fixture
def config_tables(logged_in_page):
    return ConfigTablesPage(logged_in_page)

@pytest.fixture
def connections(logged_in_page):
    return ConnectionsPage(logged_in_page)

@pytest.fixture
def purge_cdc_files(logged_in_page):
    return PurgeCdcFilesPage(logged_in_page)

@pytest.fixture
def assessment(logged_in_page):
    return AssessmentPage(logged_in_page)