"""
Theme service for token file I/O operations.

Handles:
- Writing token files to persistent storage
- Generating human-readable documentation
- Loading tokens from file system
- Managing token file updates
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from app.schemas.theme import DesignToken, TokenFile, TokenMetadata

logger = logging.getLogger(__name__)


class ThemeService:
    """Service for managing theme token files and documentation."""
    
    @staticmethod
    def write_token_file(
        token_file: TokenFile,
        output_dir: str = "ui/tokens/"
    ) -> Path:
        """Write token file to disk in JSON format."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Delete existing token files
        json_file = output_path / "epam.tokens.json"
        md_colors = output_path / "epam.colors.md"
        md_typo = output_path / "epam.typography.md"
        
        for f in [json_file, md_colors, md_typo]:
            if f.exists():
                f.unlink()
        
        # Write JSON file
        with open(json_file, 'w') as f:
            token_data = {
                "metadata": token_file.metadata.model_dump(mode='json'),
                "tokens": [token.model_dump(mode='json') for token in token_file.tokens]
            }
            json.dump(token_data, f, indent=2, default=str)
        
        logger.info(f"Wrote token file: {json_file}")
        return json_file
    
    @staticmethod
    def generate_colors_markdown(
        token_file: TokenFile,
        output_dir: str = "ui/tokens/"
    ) -> Path:
        """Generate human-readable color documentation."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        color_tokens = [
            t for t in token_file.tokens
            if t.type.value == "color" and t.status.value == "extracted"
        ]
        
        md_file = output_path / "epam.colors.md"
        with open(md_file, 'w') as f:
            f.write("# EPAM Color Tokens\n\n")
            f.write(f"Extracted: {token_file.metadata.extracted_at.isoformat()}\n")
            f.write(f"Source: {token_file.metadata.source_url}\n\n")
            
            for token in color_tokens:
                f.write(f"- **{token.name}**: `{token.value}` (from `{token.source_selector}`)\n")
            
            if not color_tokens:
                f.write("No color tokens extracted.\n")
        
        logger.info(f"Generated color documentation: {md_file}")
        return md_file
    
    @staticmethod
    def generate_typography_markdown(
        token_file: TokenFile,
        output_dir: str = "ui/tokens/"
    ) -> Path:
        """Generate human-readable typography documentation."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        typo_tokens = [
            t for t in token_file.tokens
            if t.type.value == "typography" and t.status.value == "extracted"
        ]
        
        md_file = output_path / "epam.typography.md"
        with open(md_file, 'w') as f:
            f.write("# EPAM Typography Tokens\n\n")
            f.write(f"Extracted: {token_file.metadata.extracted_at.isoformat()}\n")
            f.write(f"Source: {token_file.metadata.source_url}\n\n")
            
            for token in typo_tokens:
                f.write(f"- **{token.name}**: `{token.value}` (from `{token.source_selector}`)\n")
            
            if not typo_tokens:
                f.write("No typography tokens extracted.\n")
        
        logger.info(f"Generated typography documentation: {md_file}")
        return md_file
    
    @staticmethod
    def load_token_file(token_path: str = "ui/tokens/epam.tokens.json") -> Optional[TokenFile]:
        """Load token file from disk."""
        path = Path(token_path)
        
        if not path.exists():
            logger.error(f"Token file not found: {path}")
            raise FileNotFoundError(f"Token file not found: {path}")
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Parse as TokenFile
            token_file = TokenFile(**data)
            logger.info(f"Loaded {len(token_file.tokens)} tokens from {path}")
            return token_file
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in token file: {e}")
            raise ValueError(f"Invalid JSON in token file: {e}")
        
        except Exception as e:
            logger.error(f"Error loading token file: {e}")
            raise
