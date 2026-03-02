"""
Theme configuration service for loading and querying design tokens.

Provides:
- Loading tokens from file system at application startup
- Querying token values by name
- Validating token structure
- Reloading tokens on file updates
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from app.schemas.theme import DesignToken, TokenFile, TokenStatus

logger = logging.getLogger(__name__)


class ThemeConfig:
    """
    Backend theme configuration service.
    
    Loads extracted design tokens and provides methods to query them.
    Validates token structure and handles missing files gracefully.
    """
    
    def __init__(self, token_path: str = "ui/tokens/epam.tokens.json"):
        """
        Initialize theme configuration.
        
        Args:
            token_path: Path to epam.tokens.json file
        
        Raises:
            FileNotFoundError: If token file does not exist
            ValueError: If token file is invalid
        """
        self.token_path = token_path
        self.tokens: List[DesignToken] = []
        self.metadata = None
        self.load_tokens()
    
    def load_tokens(self) -> None:
        """Load tokens from file system."""
        path = Path(self.token_path)
        
        if not path.exists():
            logger.error(f"Token file not found: {path}")
            raise FileNotFoundError(
                f"Token file not found: {path}. "
                "Run 'python scripts/extract_epam_tokens.py' first."
            )
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Parse as TokenFile
            token_file = TokenFile(**data)
            self.tokens = token_file.tokens
            self.metadata = token_file.metadata
            
            logger.info(
                f"Loaded {len(self.tokens)} tokens from {path} "
                f"({self.metadata.tokens_extracted} extracted, "
                f"{self.metadata.tokens_unknown} unknown)"
            )
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in token file: {e}")
            raise ValueError(f"Invalid JSON in token file: {e}")
        
        except Exception as e:
            logger.error(f"Error loading token file: {e}")
            raise
    
    def reload_tokens(self) -> None:
        """Reload tokens from file system."""
        logger.info("Reloading theme tokens...")
        self.load_tokens()
    
    def get_token(self, token_name: str) -> Optional[DesignToken]:
        """
        Get token by name.
        
        Args:
            token_name: Name of the token (e.g., 'body-font-family')
        
        Returns:
            DesignToken if found, None otherwise
        """
        for token in self.tokens:
            if token.name == token_name:
                return token
        logger.warning(f"Token not found: {token_name}")
        return None
    
    def get_font_family(self, element: str = "body") -> Optional[str]:
        """
        Get font family for specified element.
        
        Args:
            element: Element name (body, h1, h2, h3)
        
        Returns:
            Font family value or None
        """
        token_name = f"{element}-fontfamily"
        token = self.get_token(token_name)
        if token and token.status.value == "extracted":
            return token.value
        return None
    
    def get_color(self, color_name: str) -> Optional[str]:
        """
        Get color token value.
        
        Args:
            color_name: Color token name (e.g., 'primary-color')
        
        Returns:
            Color value (hex) or None
        """
        token = self.get_token(color_name)
        if token and token.status.value == "extracted":
            return token.value
        return None
    
    def get_all_tokens(self) -> List[DesignToken]:
        """Get all loaded tokens."""
        return self.tokens
    
    def get_extracted_tokens(self) -> List[DesignToken]:
        """Get only successfully extracted tokens."""
        return [t for t in self.tokens if t.status == TokenStatus.EXTRACTED]
    
    def get_unknown_tokens(self) -> List[DesignToken]:
        """Get tokens that could not be extracted."""
        return [t for t in self.tokens if t.status == TokenStatus.UNKNOWN]
