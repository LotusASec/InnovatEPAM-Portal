"""
Unit tests for theme schema validation (DesignToken, TokenMetadata, ThemeConfiguration).

Tests validation rules:
- DesignToken: name uniqueness, status="extracted" requires value, status="unknown" requires evidence
- TokenMetadata: success requires tokens_extracted>0, retry_count 0-3
- ThemeConfiguration: loaded_tokens must have at least one extracted token
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.theme import (
    DesignToken,
    ThemeConfiguration,
    TokenMetadata,
    TokenStatus,
    TokenType,
)


class TestDesignTokenValidation:
    """Test DesignToken Pydantic model validation rules."""
    
    def test_valid_extracted_token(self):
        """Test creating a valid extracted token."""
        token = DesignToken(
            name="body-font-family",
            value="Open Sans, sans-serif",
            type=TokenType.TYPOGRAPHY,
            source_selector="body",
            extracted_at=datetime.now(timezone.utc),
            status=TokenStatus.EXTRACTED
        )
        assert token.name == "body-font-family"
        assert token.status == TokenStatus.EXTRACTED
        assert token.value == "Open Sans, sans-serif"
    
    def test_valid_unknown_token_with_evidence(self):
        """Test creating a valid unknown token with evidence."""
        token = DesignToken(
            name="button-hover-color",
            value=None,
            type=TokenType.COLOR,
            source_selector="button:hover",
            extracted_at=datetime.now(timezone.utc),
            status=TokenStatus.UNKNOWN,
            evidence="Hover states not extractable via computed styles",
            fallback="Darken primary by 10%"
        )
        assert token.status == TokenStatus.UNKNOWN
        assert token.evidence is not None
        assert token.fallback is not None
    
    def test_extracted_token_requires_non_empty_value(self):
        """Test that status='extracted' requires a non-empty value."""
        with pytest.raises(ValidationError) as exc_info:
            DesignToken(
                name="body-font-family",
                value="",  # Empty value should fail
                type=TokenType.TYPOGRAPHY,
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )
        
        errors = exc_info.value.errors()
        assert any("value must be non-empty" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_extracted_token_requires_value(self):
        """Test that status='extracted' requires value to be provided."""
        with pytest.raises(ValidationError) as exc_info:
            DesignToken(
                name="body-font-family",
                value=None,  # None value should fail for extracted
                type=TokenType.TYPOGRAPHY,
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )
        
        errors = exc_info.value.errors()
        assert any("value must be non-empty" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_unknown_token_requires_evidence(self):
        """Test that status='unknown' requires evidence."""
        with pytest.raises(ValidationError) as exc_info:
            DesignToken(
                name="button-hover-color",
                value=None,
                type=TokenType.COLOR,
                source_selector="button:hover",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.UNKNOWN
                # Missing evidence - should fail
            )
        
        errors = exc_info.value.errors()
        assert any("evidence is required" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_token_name_required(self):
        """Test that name field is required."""
        with pytest.raises(ValidationError):
            DesignToken(
                value="Open Sans",
                type=TokenType.TYPOGRAPHY,
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )
    
    def test_token_type_enum_validation(self):
        """Test that invalid token type is rejected."""
        with pytest.raises(ValidationError):
            DesignToken(
                name="test-token",
                value="test",
                type="invalid-type",  # Invalid enum value
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )


class TestTokenMetadataValidation:
    """Test TokenMetadata Pydantic model validation rules."""
    
    def test_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = TokenMetadata(
            source_url="https://www.epam.com/",
            extracted_at=datetime.now(timezone.utc),
            extraction_method="playwright-mcp",
            browser_version="Chromium 119.0",
            success=True,
            tokens_extracted=12,
            tokens_unknown=1,
            extraction_duration_seconds=25.5,
            retry_count=0
        )
        assert metadata.success is True
        assert metadata.tokens_extracted == 12
        assert metadata.retry_count == 0
    
    def test_success_requires_tokens_extracted(self):
        """Test that success=True requires tokens_extracted > 0."""
        with pytest.raises(ValidationError) as exc_info:
            TokenMetadata(
                source_url="https://www.epam.com/",
                extracted_at=datetime.now(timezone.utc),
                extraction_method="playwright-mcp",
                browser_version="Chromium 119.0",
                success=True,  # Success but zero tokens
                tokens_extracted=0,
                tokens_unknown=0,
                retry_count=0
            )
        
        errors = exc_info.value.errors()
        assert any("success=true requires tokens_extracted > 0" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_retry_count_valid_range(self):
        """Test that retry_count must be 0-3."""
        # Valid: retry_count=0
        metadata = TokenMetadata(
            source_url="https://www.epam.com/",
            extracted_at=datetime.now(timezone.utc),
            extraction_method="playwright-mcp",
            browser_version="Chromium 119.0",
            success=True,
            tokens_extracted=5,
            tokens_unknown=0,
            retry_count=0
        )
        assert metadata.retry_count == 0
        
        # Valid: retry_count=3
        metadata = TokenMetadata(
            source_url="https://www.epam.com/",
            extracted_at=datetime.now(timezone.utc),
            extraction_method="playwright-mcp",
            browser_version="Chromium 119.0",
            success=True,
            tokens_extracted=5,
            tokens_unknown=0,
            retry_count=3
        )
        assert metadata.retry_count == 3
    
    def test_retry_count_exceeds_max(self):
        """Test that retry_count > 3 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TokenMetadata(
                source_url="https://www.epam.com/",
                extracted_at=datetime.now(timezone.utc),
                extraction_method="playwright-mcp",
                browser_version="Chromium 119.0",
                success=False,
                tokens_extracted=0,
                tokens_unknown=0,
                retry_count=4  # Exceeds maximum
            )
        
        errors = exc_info.value.errors()
        assert any("less than or equal to 3" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_retry_count_negative(self):
        """Test that retry_count must be non-negative."""
        with pytest.raises(ValidationError):
            TokenMetadata(
                source_url="https://www.epam.com/",
                extracted_at=datetime.now(timezone.utc),
                extraction_method="playwright-mcp",
                browser_version="Chromium 119.0",
                success=False,
                tokens_extracted=0,
                tokens_unknown=0,
                retry_count=-1  # Negative not allowed
            )
    
    def test_tokens_extracted_non_negative(self):
        """Test that tokens_extracted must be non-negative."""
        with pytest.raises(ValidationError):
            TokenMetadata(
                source_url="https://www.epam.com/",
                extracted_at=datetime.now(timezone.utc),
                extraction_method="playwright-mcp",
                browser_version="Chromium 119.0",
                success=False,
                tokens_extracted=-1,  # Negative not allowed
                tokens_unknown=0,
                retry_count=0
            )


class TestThemeConfigurationValidation:
    """Test ThemeConfiguration Pydantic model validation rules."""
    
    def test_valid_theme_configuration(self):
        """Test creating valid theme configuration."""
        tokens = [
            DesignToken(
                name="body-font-family",
                value="Open Sans, sans-serif",
                type=TokenType.TYPOGRAPHY,
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )
        ]
        
        config = ThemeConfiguration(
            token_source_path="ui/tokens/epam.tokens.json",
            loaded_tokens=tokens,
            last_updated=datetime.now(timezone.utc)
        )
        
        assert config.token_source_path == "ui/tokens/epam.tokens.json"
        assert len(config.loaded_tokens) == 1
    
    def test_loaded_tokens_must_have_extracted(self):
        """Test that loaded_tokens must contain at least one 'extracted' token."""
        tokens = [
            DesignToken(
                name="button-hover-color",
                value=None,
                type=TokenType.COLOR,
                source_selector="button:hover",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.UNKNOWN,
                evidence="Not extractable"
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            ThemeConfiguration(
                token_source_path="ui/tokens/epam.tokens.json",
                loaded_tokens=tokens,  # Only unknown tokens, no extracted
                last_updated=datetime.now(timezone.utc)
            )
        
        errors = exc_info.value.errors()
        assert any("must contain at least one token with status='extracted'" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_loaded_tokens_cannot_be_empty(self):
        """Test that loaded_tokens cannot be an empty list."""
        with pytest.raises(ValidationError) as exc_info:
            ThemeConfiguration(
                token_source_path="ui/tokens/epam.tokens.json",
                loaded_tokens=[],  # Empty list
                last_updated=datetime.now(timezone.utc)
            )
        
        errors = exc_info.value.errors()
        assert any("must contain at least one token" in str(error.get('msg', '')).lower() for error in errors)
    
    def test_token_source_path_required(self):
        """Test that token_source_path is required."""
        tokens = [
            DesignToken(
                name="body-font-family",
                value="Open Sans",
                type=TokenType.TYPOGRAPHY,
                source_selector="body",
                extracted_at=datetime.now(timezone.utc),
                status=TokenStatus.EXTRACTED
            )
        ]
        
        with pytest.raises(ValidationError):
            ThemeConfiguration(
                loaded_tokens=tokens,
                last_updated=datetime.now(timezone.utc)
                # Missing token_source_path
            )
