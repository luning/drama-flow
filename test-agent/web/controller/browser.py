"""Browser lifecycle — wraps Playwright Chromium launcher."""

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserController:
    """Manages Playwright browser instance and page contexts."""

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 390,
        viewport_height: int = 844,
    ):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> Page:
        """Launch browser and return a fresh page."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(
            viewport={"width": self.viewport_width, "height": self.viewport_height}
        )
        self._page = self._context.new_page()
        return self._page

    def stop(self):
        """Clean shutdown."""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page
