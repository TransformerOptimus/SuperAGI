#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Literal

from playwright.async_api import async_playwright

from metagpt.config import CONFIG
from metagpt.logs import logger
from metagpt.utils.parse_html import WebPage


class PlaywrightWrapper:
    """Wrapper around Playwright.

    To use this module, you should have the `playwright` Python package installed and ensure that
    the required browsers are also installed. You can install playwright by running the command
    `pip install metagpt[playwright]` and download the necessary browser binaries by running the
    command `playwright install` for the first time.
    """

    def __init__(
        self,
        browser_type: Literal["chromium", "firefox", "webkit"] | None = None,
        launch_kwargs: dict | None = None,
        **kwargs,
    ) -> None:
        if browser_type is None:
            browser_type = CONFIG.playwright_browser_type
        self.browser_type = browser_type
        launch_kwargs = launch_kwargs or {}
        if CONFIG.global_proxy and "proxy" not in launch_kwargs:
            args = launch_kwargs.get("args", [])
            if not any(str.startswith(i, "--proxy-server=") for i in args):
                launch_kwargs["proxy"] = {"server": CONFIG.global_proxy}
        self.launch_kwargs = launch_kwargs
        context_kwargs = {}
        if "ignore_https_errors" in kwargs:
            context_kwargs["ignore_https_errors"] = kwargs["ignore_https_errors"]
        self._context_kwargs = context_kwargs
        self._has_run_precheck = False

    async def run(self, url: str, *urls: str) -> WebPage | list[WebPage]:
        async with async_playwright() as ap:
            browser_type = getattr(ap, self.browser_type)
            await self._run_precheck(browser_type)
            browser = await browser_type.launch(**self.launch_kwargs)
            _scrape = self._scrape

            if urls:
                return await asyncio.gather(_scrape(browser, url), *(_scrape(browser, i) for i in urls))
            return await _scrape(browser, url)

    async def _scrape(self, browser, url):
        context = await browser.new_context(**self._context_kwargs)
        page = await context.new_page()
        async with page:
            try:
                await page.goto(url)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                html = await page.content()
                inner_text = await page.evaluate("() => document.body.innerText")
            except Exception as e:
                inner_text = f"Fail to load page content for {e}"
                html = ""
            return WebPage(inner_text=inner_text, html=html, url=url)

    async def _run_precheck(self, browser_type):
        if self._has_run_precheck:
            return

        executable_path = Path(browser_type.executable_path)
        if not executable_path.exists() and "executable_path" not in self.launch_kwargs:
            kwargs = {}
            if CONFIG.global_proxy:
                kwargs["env"] = {"ALL_PROXY": CONFIG.global_proxy}
            await _install_browsers(self.browser_type, **kwargs)

            if self._has_run_precheck:
                return

            if not executable_path.exists():
                parts = executable_path.parts
                available_paths = list(Path(*parts[:-3]).glob(f"{self.browser_type}-*"))
                if available_paths:
                    logger.warning(
                        "It seems that your OS is not officially supported by Playwright. "
                        "Try to set executable_path to the fallback build version."
                    )
                    executable_path = available_paths[0].joinpath(*parts[-2:])
                    self.launch_kwargs["executable_path"] = str(executable_path)
        self._has_run_precheck = True


def _get_install_lock():
    global _install_lock
    if _install_lock is None:
        _install_lock = asyncio.Lock()
    return _install_lock


async def _install_browsers(*browsers, **kwargs) -> None:
    async with _get_install_lock():
        browsers = [i for i in browsers if i not in _install_cache]
        if not browsers:
            return
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "playwright",
            "install",
            *browsers,
            # "--with-deps",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )

        await asyncio.gather(_log_stream(process.stdout, logger.info), _log_stream(process.stderr, logger.warning))

        if await process.wait() == 0:
            logger.info("Install browser for playwright successfully.")
        else:
            logger.warning("Fail to install browser for playwright.")
        _install_cache.update(browsers)


async def _log_stream(sr, log_func):
    while True:
        line = await sr.readline()
        if not line:
            return
        log_func(f"[playwright install browser]: {line.decode().strip()}")


_install_lock: asyncio.Lock = None
_install_cache = set()


if __name__ == "__main__":
    import fire

    async def main(url: str, *urls: str, browser_type: str = "chromium", **kwargs):
        return await PlaywrightWrapper(browser_type, **kwargs).run(url, *urls)

    fire.Fire(main)
