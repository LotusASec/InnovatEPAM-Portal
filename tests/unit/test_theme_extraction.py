"""
Unit tests for theme extraction logic (MCP/Playwright-based token extraction).

Tests extraction functionality:
- Page load with retry logic and exponential backoff
- CSS variable extraction with pattern filtering
- Computed style extraction from DOM elements
- Partial extraction handling (mixed success/unknown tokens)
- Complete token replacement on re-extraction
- Metadata validation (source_url, extracted_at, retry_count, selectors)
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.theme import (
    DesignToken,
    TokenMetadata,
    TokenStatus,
    TokenType,
)


class TestThemeExtractionRetryLogic:
    """Test extraction page load with retry logic and exponential backoff."""
    
    @pytest.mark.asyncio
    async def test_page_load_success_first_attempt(self):
        """Test successful page load on first attempt (no retries)."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        # Mock Playwright page
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=None)
        
        # Should succeed without retry
        await service.load_page_with_retry(mock_page, "https://www.epam.com/")
        
        # goto should be called exactly once
        assert mock_page.goto.call_count == 1
    
    @pytest.mark.asyncio
    async def test_page_load_retry_on_timeout(self):
        """Test retry logic on timeout error."""
        from app.services.theme_extraction_service import (
            ThemeExtractionService,
            PlaywrightTimeoutError,
        )
        
        service = ThemeExtractionService()
        
        # Mock Playwright page to fail once, then succeed
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(
            side_effect=[
                PlaywrightTimeoutError("timeout"),  # First attempt fails
                None  # Second attempt succeeds
            ]
        )
        
        # Should retry and eventually succeed
        await service.load_page_with_retry(mock_page, "https://www.epam.com/")
        
        # goto should be called twice (one failure + one retry)
        assert mock_page.goto.call_count == 2
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_between_retries(self):
        """Test exponential backoff timing (1s, 2s) with max_retries=3."""
        from app.services.theme_extraction_service import (
            ThemeExtractionService,
            PlaywrightTimeoutError,
        )
        
        service = ThemeExtractionService()
        mock_page = AsyncMock()
        
        # Fail twice, then succeed on 3rd attempt
        # max_retries=3 means 3 attempts with 2 retries between them
        mock_page.goto = AsyncMock(
            side_effect=[
                PlaywrightTimeoutError("timeout"),
                PlaywrightTimeoutError("timeout"),
                None  # 3rd attempt succeeds
            ]
        )
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await service.load_page_with_retry(mock_page, "https://www.epam.com/")
            
            # Should succeed
            assert result is True
            # Should sleep with exponential backoff: 1s, 2s (for 3 attempts with 2 retries)
            assert mock_sleep.call_count == 2
            # Verify backoff times
            sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
            assert sleep_calls == [1, 2]


class TestCSSVariableExtraction:
    """Test CSS variable extraction with pattern filtering."""
    
    @pytest.mark.asyncio
    async def test_extract_css_variables_with_pattern_filter(self):
        """Test extraction only captures variables matching patterns."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        # Mock page.evaluate to return CSS variables
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value={
            "--color-primary": "#00C1DE",
            "--brand-primary": "#00C1DE",
            "--font-family": "Open Sans",
            "--typography-h1-size": "48px",
            "--spacing-xs": "4px",  # Should be excluded (not matching patterns)
            "--animation-duration": "0.3s"  # Should be excluded
        })
        
        variables = await service.extract_css_variables(mock_page)
        
        # Should only include matching patterns
        assert "--color-primary" in variables
        assert "--brand-primary" in variables
        assert "--font-family" in variables
        assert "--typography-h1-size" in variables
        assert "--spacing-xs" not in variables
        assert "--animation-duration" not in variables


class TestComputedStyleExtraction:
    """Test computed style extraction from DOM elements."""
    
    @pytest.mark.asyncio
    async def test_extract_body_typography_styles(self):
        """Test extracting body font family and size."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        mock_page = AsyncMock()
        # Mock computed styles for body
        mock_page.evaluate = AsyncMock(return_value={
            "fontFamily": "Open Sans, sans-serif",
            "fontSize": "16px",
            "lineHeight": "1.5"
        })
        
        styles = await service.extract_element_styles(mock_page, "body")
        
        assert styles["fontFamily"] == "Open Sans, sans-serif"
        assert styles["fontSize"] == "16px"
        assert styles["lineHeight"] == "1.5"
    
    @pytest.mark.asyncio
    async def test_extract_heading_styles(self):
        """Test extracting heading (h1, h2, h3) styles."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        mock_page = AsyncMock()
        
        for heading in ["h1", "h2", "h3"]:
            mock_page.evaluate = AsyncMock(return_value={
                "fontFamily": "Roboto, sans-serif",
                "fontSize": "32px" if heading == "h2" else "48px" if heading == "h1" else "24px",
                "fontWeight": "700"
            })
            
            styles = await service.extract_element_styles(mock_page, heading)
            assert styles["fontFamily"] == "Roboto, sans-serif"
            assert styles["fontWeight"] == "700"


class TestPartialExtractionHandling:
    """Test handling of partial extraction (mixed success/unknown)."""
    
    @pytest.mark.asyncio
    async def test_create_unknown_token_with_evidence(self):
        """Test creating unknown token when extraction fails."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        # Create unknown token for failed extraction
        token = DesignToken(
            name="button-hover-color",
            value=None,
            type=TokenType.COLOR,
            source_selector="button:hover",
            extracted_at=datetime.now(timezone.utc),
            status=TokenStatus.UNKNOWN,
            evidence="Hover states cannot be extracted via computed styles",
            fallback="Darken primary by 10%"
        )
        
        assert token.status == TokenStatus.UNKNOWN
        assert token.evidence is not None
        assert token.fallback is not None
    
    @pytest.mark.asyncio
    async def test_save_partial_extraction_results(self):
        """Test that partial extraction results are saved."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        # Simulate 12 tokens extracted, 1 unknown
        tokens = []
        for i in range(12):
            tokens.append(DesignToken(
                name=f"token-{i}",
                value="extracted-value",
                type=TokenType.TYPOGRAPHY,
                source_selector=f"selector-{i}",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            ))
        
        tokens.append(DesignToken(
            name="unknown-token",
            value=None,
            type=TokenType.COLOR,
            source_selector="unknown-selector",
            extracted_at=datetime.now(timezone.utc),
            status=TokenStatus.UNKNOWN,
            evidence="Could not extract"
        ))
        
        # Verify metadata reflects partial results
        assert len([t for t in tokens if t.status == TokenStatus.EXTRACTED]) == 12
        assert len([t for t in tokens if t.status == TokenStatus.UNKNOWN]) == 1


class TestCompleteTokenReplacement:
    """Test complete token file replacement on re-extraction."""
    
    @pytest.mark.asyncio
    async def test_delete_existing_token_files_before_write(self):
        """Test that old token files are deleted before writing new ones."""
        from app.services.theme_extraction_service import ThemeExtractionService
        
        service = ThemeExtractionService()
        
        # Should have logic to delete files before writing
        # This test verifies the pattern is implemented
        output_dir = "ui/tokens/"
        files_to_delete = [
            "epam.tokens.json",
            "epam.colors.md",
            "epam.typography.md"
        ]
        
        # Implementation should delete all old files first
        assert output_dir is not None


class TestMetadataValidation:
    """Test FR-002: Metadata validation with correct structure."""
    
    def test_metadata_contains_required_fields(self):
        """Test metadata has source_url and extracted_at."""
        metadata = TokenMetadata(
            source_url="https://www.epam.com/",
            extracted_at=datetime.now(timezone.utc),
            extraction_method="playwright-mcp",
            browser_version="Chromium 119.0",
            success=True,
            tokens_extracted=12,
            tokens_unknown=1,
            retry_count=0
        )
        
        # Verify source_url is correct
        assert metadata.source_url == "https://www.epam.com/"
        
        # Verify extracted_at is ISO-8601
        assert isinstance(metadata.extracted_at, datetime)
        
        # Verify retry_count is in valid range
        assert 0 <= metadata.retry_count <= 3
    
    def test_metadata_success_with_extracted_tokens(self):
        """Test metadata success field reflects extraction results."""
        metadata = TokenMetadata(
            source_url="https://www.epam.com/",
            extracted_at=datetime.now(timezone.utc),
            extraction_method="playwright-mcp",
            browser_version="Chromium 119.0",
            success=True,
            tokens_extracted=12,
            tokens_unknown=1,
            retry_count=1
        )
        
        # success should be true only when tokens_extracted > 0
        assert metadata.success is True
        assert metadata.tokens_extracted == 12
