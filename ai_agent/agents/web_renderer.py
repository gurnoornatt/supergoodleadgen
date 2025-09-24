#!/usr/bin/env python3
"""
Async Playwright Web Content Renderer

Efficiently renders JavaScript-heavy gym websites with parallel processing,
resource blocking, and comprehensive error handling.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeout,
    Error as PlaywrightError
)


@dataclass
class RenderResult:
    """Result of a website rendering operation"""
    url: str
    success: bool
    html_content: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    render_time_seconds: Optional[float] = None
    title: Optional[str] = None
    final_url: Optional[str] = None


class RenderError(Exception):
    """Custom exception for rendering errors"""
    pass


class AsyncWebRenderer:
    """
    Async Playwright-based web renderer with worker pool for parallel processing

    Features:
    - Parallel website rendering with worker pool
    - Resource blocking for faster loading (images, CSS, fonts)
    - 15-second navigation timeout
    - Comprehensive error handling
    - Proper browser context isolation
    - Memory leak prevention with cleanup
    """

    def __init__(self,
                 max_workers: int = 5,
                 timeout_seconds: int = 15,
                 headless: bool = True,
                 block_resources: bool = True,
                 user_agent: Optional[str] = None):
        """
        Initialize AsyncWebRenderer

        Args:
            max_workers: Maximum number of concurrent browser contexts
            timeout_seconds: Navigation timeout in seconds (default: 15)
            headless: Run browser in headless mode
            block_resources: Block images, CSS, fonts for faster loading
            user_agent: Custom user agent string
        """
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds * 1000  # Convert to milliseconds for Playwright
        self.headless = headless
        self.block_resources = block_resources
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Runtime state
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._semaphore: Optional[asyncio.Semaphore] = None

        # Statistics
        self._stats = {
            'total_requests': 0,
            'successful_renders': 0,
            'failed_renders': 0,
            'timeout_errors': 0,
            'connection_errors': 0,
            'other_errors': 0,
            'total_render_time': 0.0
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.close()

    async def start(self):
        """Initialize Playwright browser and resources"""
        self.logger.info(f"Starting AsyncWebRenderer with {self.max_workers} workers")

        # Initialize semaphore for worker pool
        self._semaphore = asyncio.Semaphore(self.max_workers)

        # Launch Playwright
        self._playwright = await async_playwright().start()

        # Launch browser with optimized settings
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding'
            ]
        )

        self.logger.info("Playwright browser launched successfully")

    async def close(self):
        """Clean up browser and Playwright resources"""
        self.logger.info("Closing AsyncWebRenderer")

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self.logger.info("AsyncWebRenderer closed successfully")

    async def _setup_resource_blocking(self, page: Page):
        """Configure resource blocking for faster page loading"""
        if not self.block_resources:
            return

        blocked_types = {"image", "stylesheet", "font", "media", "manifest"}

        async def block_unnecessary_resources(route):
            """Block unnecessary resource types"""
            try:
                if route.request.resource_type in blocked_types:
                    await route.abort()
                else:
                    await route.continue_()
            except Exception as e:
                self.logger.warning(f"Route blocking error: {e}")
                try:
                    await route.continue_()
                except Exception:
                    pass  # Route may already be handled

        await page.route("**/*", block_unnecessary_resources)

    async def _render_single_website(self, url: str) -> RenderResult:
        """
        Render a single website with error handling

        Args:
            url: Website URL to render

        Returns:
            RenderResult with render outcome
        """
        start_time = time.time()

        # Validate URL format
        if not url or not isinstance(url, str):
            return RenderResult(
                url=str(url),
                success=False,
                error_message="Invalid URL provided",
                error_type="validation_error"
            )

        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        # Acquire semaphore for worker pool
        async with self._semaphore:
            context = None
            page = None

            try:
                # Create isolated browser context
                context = await self._browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    ignore_https_errors=True,
                    java_script_enabled=True,
                )

                # Create page
                page = await context.new_page()

                # Setup resource blocking
                await self._setup_resource_blocking(page)

                # Navigate to page with timeout
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=self.timeout_seconds
                )

                # Check if navigation was successful
                if response and response.status >= 400:
                    return RenderResult(
                        url=url,
                        success=False,
                        error_message=f"HTTP {response.status}",
                        error_type="http_error",
                        render_time_seconds=time.time() - start_time,
                        final_url=page.url
                    )

                # Wait a bit for dynamic content
                try:
                    await page.wait_for_timeout(1000)  # 1 second
                except Exception:
                    pass  # Continue if wait fails

                # Extract page content
                html_content = await page.content()
                title = await page.title()
                final_url = page.url

                render_time = time.time() - start_time

                return RenderResult(
                    url=url,
                    success=True,
                    html_content=html_content,
                    title=title,
                    final_url=final_url,
                    render_time_seconds=render_time
                )

            except PlaywrightTimeout:
                return RenderResult(
                    url=url,
                    success=False,
                    error_message=f"Navigation timeout after {self.timeout_seconds/1000}s",
                    error_type="timeout_error",
                    render_time_seconds=time.time() - start_time
                )

            except PlaywrightError as e:
                # Handle specific Playwright errors
                error_msg = str(e).lower()
                if "net::err_name_not_resolved" in error_msg:
                    error_type = "dns_error"
                elif "net::err_connection_refused" in error_msg:
                    error_type = "connection_refused"
                elif "net::err_timed_out" in error_msg:
                    error_type = "connection_timeout"
                else:
                    error_type = "playwright_error"

                return RenderResult(
                    url=url,
                    success=False,
                    error_message=str(e),
                    error_type=error_type,
                    render_time_seconds=time.time() - start_time
                )

            except Exception as e:
                return RenderResult(
                    url=url,
                    success=False,
                    error_message=str(e),
                    error_type="unexpected_error",
                    render_time_seconds=time.time() - start_time
                )

            finally:
                # Ensure proper cleanup
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass

                if context:
                    try:
                        await context.close()
                    except Exception:
                        pass

    async def render_websites(self, urls: List[str]) -> List[RenderResult]:
        """
        Render multiple websites in parallel

        Args:
            urls: List of URLs to render

        Returns:
            List of RenderResult objects
        """
        if not urls:
            return []

        if not self._browser:
            raise RenderError("Renderer not started - call start() or use as context manager")

        self.logger.info(f"Rendering {len(urls)} websites with {self.max_workers} workers")

        # Create tasks for parallel processing
        tasks = [self._render_single_website(url) for url in urls]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and update statistics
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions from gather
                processed_results.append(RenderResult(
                    url=urls[i],
                    success=False,
                    error_message=str(result),
                    error_type="execution_error"
                ))
            else:
                processed_results.append(result)

        # Update statistics
        self._update_statistics(processed_results)

        self.logger.info(
            f"Completed rendering: {self._stats['successful_renders']} successful, "
            f"{self._stats['failed_renders']} failed"
        )

        return processed_results

    def _update_statistics(self, results: List[RenderResult]):
        """Update rendering statistics"""
        for result in results:
            self._stats['total_requests'] += 1

            if result.success:
                self._stats['successful_renders'] += 1
            else:
                self._stats['failed_renders'] += 1

                # Categorize errors
                if result.error_type == "timeout_error":
                    self._stats['timeout_errors'] += 1
                elif result.error_type in ["dns_error", "connection_refused", "connection_timeout"]:
                    self._stats['connection_errors'] += 1
                else:
                    self._stats['other_errors'] += 1

            if result.render_time_seconds:
                self._stats['total_render_time'] += result.render_time_seconds

    def get_statistics(self) -> Dict:
        """Get rendering statistics"""
        stats = self._stats.copy()

        # Calculate derived metrics
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_renders'] / stats['total_requests']
            stats['average_render_time'] = stats['total_render_time'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
            stats['average_render_time'] = 0.0

        return stats

    def reset_statistics(self):
        """Reset rendering statistics"""
        self._stats = {
            'total_requests': 0,
            'successful_renders': 0,
            'failed_renders': 0,
            'timeout_errors': 0,
            'connection_errors': 0,
            'other_errors': 0,
            'total_render_time': 0.0
        }


# Convenience function for simple usage
async def render_websites_simple(urls: List[str],
                                 max_workers: int = 5,
                                 timeout_seconds: int = 15,
                                 block_resources: bool = True) -> List[RenderResult]:
    """
    Simple function to render websites without managing renderer lifecycle

    Args:
        urls: List of URLs to render
        max_workers: Number of concurrent workers
        timeout_seconds: Navigation timeout
        block_resources: Whether to block images/CSS/fonts

    Returns:
        List of RenderResult objects
    """
    async with AsyncWebRenderer(
        max_workers=max_workers,
        timeout_seconds=timeout_seconds,
        block_resources=block_resources
    ) as renderer:
        return await renderer.render_websites(urls)


if __name__ == "__main__":
    # Example usage for testing

    logging.basicConfig(level=logging.INFO)

    async def test_renderer():
        """Test the renderer with sample URLs"""
        test_urls = [
            "https://example.com",
            "https://httpbin.org/delay/2",
            "https://httpstat.us/404",
            "https://nonexistent-gym-website-test.com",
            "https://google.com"
        ]

        results = await render_websites_simple(test_urls, max_workers=3)

        print("\n=== Render Results ===")
        for result in results:
            status = "✓" if result.success else "✗"
            print(f"{status} {result.url}")
            if result.success:
                print(f"  Title: {result.title}")
                print(f"  HTML size: {len(result.html_content)} chars")
                print(f"  Render time: {result.render_time_seconds:.2f}s")
            else:
                print(f"  Error: {result.error_message}")
            print()

    # Run test if executed directly
    asyncio.run(test_renderer())
