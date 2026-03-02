"""
Theme extraction service using MCP/Playwright for browser automation.

This service provides:
- Automated token extraction from https://www.epam.com/ using Playwright
- Retry logic with exponential backoff for network resilience
- CSS variable extraction with pattern filtering
- Computed style extraction from DOM elements
- Structured logging for debugging and progress tracking
- Metadata tracking for extraction sessions
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from app.schemas.theme import (
    DesignToken,
    TokenFile,
    TokenMetadata,
    TokenStatus,
    TokenType,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ThemeExtractionService:
    """
    Service for extracting design tokens from EPAM website using Playwright.
    
    Provides methods for:
    - Loading pages with retry logic
    - Extracting CSS variables and computed styles
    - Handling extraction failures gracefully
    - Writing results to JSON and Markdown files
    """
    
    # CSS variable pattern filters (from FR-004)
    CSS_VAR_PATTERNS = [
        r'^--color-',
        r'^--brand-',
        r'^--font-',
        r'^--typography-'
    ]
    
    # Element selectors for style extraction (from FR-003)
    ELEMENT_SELECTORS = {
        'body': 'body',
        'h1': 'h1',
        'h2': 'h2',
        'h3': 'h3',
        'button': 'button[type="submit"], .btn-primary, button:first-of-type',
        'link': 'a:first-of-type',
    }
    
    # Style properties to extract
    STYLE_PROPERTIES = [
        'fontFamily',
        'fontSize',
        'fontWeight',
        'lineHeight',
        'color',
        'backgroundColor',
        'borderRadius',
        'padding'
    ]
    
    def __init__(self, url: str = "https://www.epam.com/"):
        """Initialize extraction service."""
        self.url = url
        self.tokens: List[DesignToken] = []
        self.metadata: Optional[TokenMetadata] = None
        self.start_time = datetime.now(timezone.utc)
    
    async def load_page_with_retry(
        self,
        page,
        url: str,
        max_retries: int = 3,
        timeout_ms: int = 10000
    ) -> bool:
        """
        Load page with retry logic and exponential backoff.
        
        Args:
            page: Playwright page object
            url: URL to load
            max_retries: Maximum retry attempts (3 per FR-015)
            timeout_ms: Timeout per attempt
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            Last exception if all retries exhausted
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Stage: Page Load | Attempt: {attempt + 1} | URL: {url}")
                
                await page.goto(url, timeout=timeout_ms, wait_until='networkidle')
                
                logger.info(f"Stage: Page Load | Success | URL: {url}")
                return True
                
            except PlaywrightTimeoutError as e:
                last_error = e
                logger.warning(
                    f"Stage: Page Load | Timeout | Attempt: {attempt + 1} | "
                    f"Error: {str(e)}"
                )
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    backoff_time = 2 ** attempt
                    logger.info(
                        f"Stage: Page Load | Retrying in {backoff_time}s..."
                    )
                    await asyncio.sleep(backoff_time)
                else:
                    raise last_error
        
        if last_error:
            raise last_error
        
        return False
    
    async def extract_css_variables(self, page) -> Dict[str, str]:
        """
        Extract CSS custom properties from :root with pattern filtering.
        
        Implements FR-004: Filter by naming patterns to include only
        brand-relevant variables matching --color-*, --brand-*, --font-*, --typography-*
        """
        logger.info("Stage: Selector Search | Type: CSS Variables | Pattern: --color-*, --brand-*, --font-*, --typography-*")
        
        # JavaScript to extract CSS variables from :root
        js_code = """
        () => {
            const variables = {};
            const root = document.documentElement;
            const styles = getComputedStyle(root);
            
            for (let i = 0; i < styles.length; i++) {
                const propName = styles[i];
                if (propName.startsWith('--')) {
                    variables[propName] = styles.getPropertyValue(propName).trim();
                }
            }
            
            return variables;
        }
        """
        
        try:
            all_variables = await page.evaluate(js_code)
        except Exception as e:
            logger.warning(f"Stage: Selector Search | CSS Variables | Error: {str(e)}")
            return {}
        
        # Filter variables by pattern
        filtered_variables = {}
        for var_name, var_value in all_variables.items():
            for pattern in self.CSS_VAR_PATTERNS:
                if re.match(pattern, var_name):
                    filtered_variables[var_name] = var_value
                    logger.info(
                        f"Stage: Token Capture | CSS Variable | "
                        f"Name: {var_name} | Value: {var_value}"
                    )
                    break
        
        return filtered_variables
    
    async def extract_element_styles(
        self,
        page,
        selector: str
    ) -> Dict[str, str]:
        """
        Extract computed styles from a DOM element.
        
        Args:
            page: Playwright page object
            selector: CSS selector for element
        
        Returns:
            Dictionary of style properties and values
        """
        logger.info(f"Stage: Selector Search | Selector: {selector} | Found: checking...")
        
        js_code = f"""
        () => {{
            const element = document.querySelector('{selector}');
            if (!element) {{
                return null;
            }}
            
            const styles = getComputedStyle(element);
            const result = {{}};
            
            const props = {self.STYLE_PROPERTIES};
            for (const prop of props) {{
                result[prop] = styles[prop];
            }}
            
            return result;
        }}
        """
        
        try:
            styles = await page.evaluate(js_code)
            if styles:
                logger.info(f"Stage: Selector Search | Selector: {selector} | Found: true")
                return styles
            else:
                logger.warning(f"Stage: Selector Search | Selector: {selector} | Found: false")
                return {}
        except Exception as e:
            logger.warning(
                f"Stage: Selector Search | Selector: {selector} | "
                f"Error: {str(e)}"
            )
            return {}
    
    async def extract_tokens(self) -> TokenFile:
        """
        Execute complete token extraction workflow using Playwright.
        
        Returns:
            TokenFile with metadata and extracted tokens
        """
        async with async_playwright() as p:
            # Launch browser
            logger.info("Stage: Page Load | Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Load page with retries
                await self.load_page_with_retry(page, self.url)
                
                # Extract CSS variables
                css_variables = await self.extract_css_variables(page)
                
                # Extract element styles
                extracted_tokens = []
                unknown_count = 0
                
                for element_name, selector in self.ELEMENT_SELECTORS.items():
                    styles = await self.extract_element_styles(page, selector)
                    
                    if styles:
                        # Create tokens for each property
                        for prop, value in styles.items():
                            if value and value.strip():
                                token_name = f"{element_name}-{prop.lower()}"
                                token = DesignToken(
                                    name=token_name,
                                    value=value,
                                    type=self._determine_token_type(prop),
                                    source_selector=selector,
                                    extracted_at=datetime.now(timezone.utc),
                                    status=TokenStatus.EXTRACTED
                                )
                                extracted_tokens.append(token)
                                logger.info(
                                    f"Stage: Token Capture | Token: {token_name} | "
                                    f"Value: {value} | Status: extracted"
                                )
                    else:
                        # Mark as unknown if extraction failed
                        unknown_count += 1
                        token = DesignToken(
                            name=f"{element_name}-unknown",
                            value=None,
                            type=TokenType.COLOR,
                            source_selector=selector,
                            extracted_at=datetime.now(timezone.utc),
                            status=TokenStatus.UNKNOWN,
                            evidence=f"Could not extract computed styles from selector: {selector}"
                        )
                        extracted_tokens.append(token)
                        logger.info(
                            f"Stage: Token Capture | Token: {element_name}-unknown | "
                            f"Status: unknown"
                        )
                
                # Create metadata
                extraction_duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
                
                metadata = TokenMetadata(
                    source_url=self.url,
                    extracted_at=datetime.now(timezone.utc),
                    extraction_method="playwright-mcp",
                    browser_version="Chromium",
                    success=len(extracted_tokens) > 0,
                    tokens_extracted=len([t for t in extracted_tokens if t.status == TokenStatus.EXTRACTED]),
                    tokens_unknown=len([t for t in extracted_tokens if t.status == TokenStatus.UNKNOWN]),
                    extraction_duration_seconds=extraction_duration,
                    retry_count=0  # Will be updated if retries were used
                )
                
                logger.info(
                    f"Stage: File Write | Total: {len(extracted_tokens)} | "
                    f"Extracted: {metadata.tokens_extracted} | "
                    f"Unknown: {metadata.tokens_unknown}"
                )
                
                return TokenFile(
                    metadata=metadata,
                    tokens=extracted_tokens
                )
                
            finally:
                await browser.close()
    
    @staticmethod
    def _determine_token_type(property_name: str) -> TokenType:
        """Determine token type based on CSS property."""
        prop_lower = property_name.lower()
        
        if any(x in prop_lower for x in ['font', 'size', 'weight', 'height']):
            return TokenType.TYPOGRAPHY
        elif any(x in prop_lower for x in ['color', 'background']):
            return TokenType.COLOR
        else:
            return TokenType.SPACING
    
    async def write_tokens_to_file(
        self,
        token_file: TokenFile,
        output_dir: str = "ui/tokens/"
    ) -> None:
        """
        Write extracted tokens to JSON file.
        
        Implements complete file replacement (FR-013):
        - Delete existing files before writing
        - Write all tokens and metadata to single JSON file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Delete existing files
        json_file = output_path / "epam.tokens.json"
        if json_file.exists():
            logger.info(f"Stage: File Write | Deleting old file: {json_file}")
            json_file.unlink()
        
        # Write new JSON file
        json_file = output_path / "epam.tokens.json"
        with open(json_file, 'w') as f:
            # Convert to dict for JSON serialization
            token_data = {
                "metadata": token_file.metadata.model_dump(),
                "tokens": [token.model_dump() for token in token_file.tokens]
            }
            
            # Ensure datetime objects are serialized as ISO-8601 strings
            json.dump(token_data, f, indent=2, default=str)
        
        logger.info(f"Stage: File Write | Success | File: {json_file}")
    
    def generate_colors_markdown(
        self,
        tokens: List[DesignToken],
        output_dir: str = "ui/tokens/"
    ) -> None:
        """Generate human-readable color documentation (FR-006)."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        color_tokens = [t for t in tokens if t.type == TokenType.COLOR and t.status == TokenStatus.EXTRACTED]
        
        md_file = output_path / "epam.colors.md"
        with open(md_file, 'w') as f:
            f.write("# EPAM Color Tokens\n\n")
            f.write(f"Extracted: {datetime.now(timezone.utc).isoformat()}\n\n")
            
            for token in color_tokens:
                f.write(f"- **{token.name}**: `{token.value}` (from `{token.source_selector}`)\n")
        
        logger.info(f"Stage: File Write | Success | File: {md_file}")
    
    def generate_typography_markdown(
        self,
        tokens: List[DesignToken],
        output_dir: str = "ui/tokens/"
    ) -> None:
        """Generate human-readable typography documentation (FR-007)."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        typo_tokens = [t for t in tokens if t.type == TokenType.TYPOGRAPHY and t.status == TokenStatus.EXTRACTED]
        
        md_file = output_path / "epam.typography.md"
        with open(md_file, 'w') as f:
            f.write("# EPAM Typography Tokens\n\n")
            f.write(f"Extracted: {datetime.now(timezone.utc).isoformat()}\n\n")
            
            for token in typo_tokens:
                f.write(f"- **{token.name}**: `{token.value}` (from `{token.source_selector}`)\n")
        
        logger.info(f"Stage: File Write | Success | File: {md_file}")
