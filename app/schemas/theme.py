"""
Theme-related Pydantic schemas for EPAM UI token extraction and validation.

This module defines data models for:
- DesignToken: Individual design decisions (colors, typography)
- TokenMetadata: Extraction session metadata
- ThemeConfiguration: Backend theme service configuration
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TokenType(str, Enum):
    """Design token category enumeration."""
    TYPOGRAPHY = "typography"
    COLOR = "color"
    SPACING = "spacing"


class TokenStatus(str, Enum):
    """Token extraction status enumeration."""
    EXTRACTED = "extracted"
    UNKNOWN = "unknown"


class DesignToken(BaseModel):
    """
    Represents a single design decision extracted from the EPAM website.
    
    Attributes:
        name: Token identifier (e.g., "body-font-family")
        value: Token value (e.g., "Open Sans, sans-serif")
        type: Category of token (typography, color, spacing)
        source_selector: CSS selector used for extraction
        extracted_at: Timestamp when token was captured
        status: Extraction status (extracted or unknown)
        evidence: DOM snippet when status is unknown
        fallback: Suggested fallback value when status is unknown
    """
    name: str = Field(..., min_length=1, description="Unique token identifier")
    value: Optional[str] = Field(None, description="Token value")
    type: TokenType = Field(..., description="Token category")
    source_selector: str = Field(..., min_length=1, description="CSS selector for extraction")
    extracted_at: datetime = Field(..., description="Extraction timestamp")
    status: TokenStatus = Field(..., description="Extraction status")
    evidence: Optional[str] = Field(None, description="Evidence when status is unknown")
    fallback: Optional[str] = Field(None, description="Fallback value when status is unknown")

    @model_validator(mode='after')
    def validate_extracted_token_has_value(self):
        """Ensure value is non-empty when status is extracted."""
        if self.status == TokenStatus.EXTRACTED:
            if not self.value or not self.value.strip():
                raise ValueError("value must be non-empty when status is 'extracted'")
        return self

    @model_validator(mode='after')
    def validate_evidence_for_unknown(self):
        """Ensure evidence is provided when status is unknown."""
        if self.status == TokenStatus.UNKNOWN and not self.evidence:
            raise ValueError("evidence is required when status is 'unknown'")
        return self


class TokenMetadata(BaseModel):
    """
    Captures context about an extraction session.
    
    Attributes:
        source_url: Website from which tokens were extracted
        extracted_at: Extraction session timestamp
        extraction_method: Method used (e.g., "playwright-mcp")
        browser_version: Browser used for extraction
        success: Overall extraction success indicator
        tokens_extracted: Count of successfully extracted tokens
        tokens_unknown: Count of tokens marked as unknown
        extraction_duration_seconds: Total extraction time
        retry_count: Number of retries attempted (0-3)
    """
    source_url: str = Field(..., description="Source website URL")
    extracted_at: datetime = Field(..., description="Extraction timestamp")
    extraction_method: str = Field(..., description="Extraction method identifier")
    browser_version: str = Field(..., description="Browser version used")
    success: bool = Field(..., description="Overall extraction success")
    tokens_extracted: int = Field(..., ge=0, description="Count of extracted tokens")
    tokens_unknown: int = Field(..., ge=0, description="Count of unknown tokens")
    extraction_duration_seconds: Optional[float] = Field(None, ge=0, description="Extraction duration")
    retry_count: Optional[int] = Field(0, ge=0, le=3, description="Retry count (0-3)")

    @model_validator(mode='after')
    def validate_success_requires_tokens(self):
        """Ensure success=True requires at least one extracted token."""
        if self.success and self.tokens_extracted == 0:
            raise ValueError("success=true requires tokens_extracted > 0")
        return self


class ThemeConfiguration(BaseModel):
    """
    Backend service configuration for loading and validating design tokens.
    
    Attributes:
        token_source_path: Path to token JSON file
        loaded_tokens: Array of loaded DesignToken objects
        last_updated: Timestamp when tokens were last loaded
    """
    token_source_path: str = Field(..., min_length=1, description="Path to token JSON file")
    loaded_tokens: List[DesignToken] = Field(..., description="Loaded design tokens")
    last_updated: datetime = Field(..., description="Last load timestamp")

    @field_validator('loaded_tokens')
    @classmethod
    def validate_has_extracted_tokens(cls, v):
        """Ensure at least one token has status='extracted'."""
        if not v:
            raise ValueError("loaded_tokens must contain at least one token")
        
        has_extracted = any(token.status == TokenStatus.EXTRACTED for token in v)
        if not has_extracted:
            raise ValueError("loaded_tokens must contain at least one token with status='extracted'")
        
        return v


class TokenFile(BaseModel):
    """
    Complete token file structure (metadata + tokens).
    
    This represents the JSON file format stored in ui/tokens/epam.tokens.json.
    """
    metadata: TokenMetadata
    tokens: List[DesignToken]
