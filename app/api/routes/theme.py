"""
FastAPI routes for theme preview endpoint.

Provides:
- GET /api/theme/preview - Preview page with all themed components
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.core.theme_config import ThemeConfig
from app.schemas.theme import DesignToken, TokenStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/theme", tags=["theme"])

# Global theme config instance
_theme_config: Optional[ThemeConfig] = None


def get_theme_config() -> ThemeConfig:
    """Get or initialize global theme config."""
    global _theme_config
    if _theme_config is None:
        try:
            _theme_config = ThemeConfig()
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load theme config: {e}")
            raise
    return _theme_config


@router.get("/preview", response_class=HTMLResponse)
async def preview_theme() -> str:
    """
    Serve theme preview page with all components styled with extracted tokens.
    
    Response:
        HTML page with typography, buttons, form elements, and links styled
        with tokens from ui/tokens/epam.tokens.json
    """
    try:
        theme_config = get_theme_config()
    except Exception as e:
        logger.error(f"Theme configuration error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Theme configuration error: {str(e)}"
        )
    
    # Extract tokens for styling
    tokens = theme_config.get_all_tokens()
    
    # Build CSS from tokens
    css_styles = _generate_styles_from_tokens(tokens)
    
    # Get metadata for footer
    metadata = theme_config.metadata
    
    # Build HTML response
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPAM Theme Preview</title>
    <style>
        {css_styles}
        
        body {{
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 2rem;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #0071c5;
            margin-bottom: 2rem;
        }}
        
        h2 {{
            color: #0071c5;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #0071c5;
            padding-bottom: 0.5rem;
        }}
        
        section {{
            background: white;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .sample {{
            margin: 1rem 0;
            padding: 1rem;
            background-color: #f9f9f9;
            border-left: 4px solid #0071c5;
        }}
        
        .typography-sample {{
            margin: 1.5rem 0;
        }}
        
        .button-group {{
            margin: 1rem 0;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        button {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        button.primary {{
            background-color: #0071c5;
            color: white;
        }}
        
        button.primary:hover {{
            background-color: #005fa3;
        }}
        
        button.secondary {{
            background-color: #e0e0e0;
            color: #333;
        }}
        
        button.secondary:hover {{
            background-color: #d0d0d0;
        }}
        
        button:disabled {{
            background-color: #ccc;
            color: #999;
            cursor: not-allowed;
        }}
        
        input, textarea {{
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 1rem;
            margin: 0.5rem 0;
            width: 100%;
            box-sizing: border-box;
        }}
        
        input:focus, textarea:focus {{
            outline: none;
            border-color: #0071c5;
            box-shadow: 0 0 0 3px rgba(0, 113, 197, 0.1);
        }}
        
        a {{
            color: #0071c5;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        footer {{
            background: white;
            padding: 2rem;
            border-top: 1px solid #ddd;
            color: #666;
            text-align: center;
            margin-top: 3rem;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 0 0.25rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        .token-info {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>EPAM Theme Preview</h1>
        <p>Visual preview of extracted EPAM design tokens and theme application.</p>
        
        <section>
            <h2>Typography</h2>
            
            <div class="typography-sample">
                <h3>Body Text (Regular)</h3>
                <p>This is a sample of body text using the extracted EPAM typography settings. 
                   It demonstrates how normal paragraph text appears with the theme applied.</p>
                <div class="token-info">
                    Font: {_get_token_value(tokens, 'body-fontfamily', 'System default')} | 
                    Size: {_get_token_value(tokens, 'body-fontsize', 'inherit')}
                </div>
            </div>
            
            <div class="typography-sample">
                <h1>Heading 1</h1>
                <div class="token-info">Font: {_get_token_value(tokens, 'h1-fontfamily', 'System default')} | 
                    Size: {_get_token_value(tokens, 'h1-fontsize', 'inherit')}</div>
            </div>
            
            <div class="typography-sample">
                <h2 style="border: none;">Heading 2</h2>
                <div class="token-info">Font: {_get_token_value(tokens, 'h2-fontfamily', 'System default')} | 
                    Size: {_get_token_value(tokens, 'h2-fontsize', 'inherit')}</div>
            </div>
            
            <div class="typography-sample">
                <h3>Heading 3</h3>
                <div class="token-info">Font: {_get_token_value(tokens, 'h3-fontfamily', 'System default')} | 
                    Size: {_get_token_value(tokens, 'h3-fontsize', 'inherit')}</div>
            </div>
        </section>
        
        <section>
            <h2>Buttons</h2>
            <div class="button-group">
                <button class="primary">Primary Button</button>
                <button class="secondary">Secondary Button</button>
                <button disabled>Disabled Button</button>
            </div>
        </section>
        
        <section>
            <h2>Form Elements</h2>
            <div>
                <label for="input-text">Text Input:</label>
                <input id="input-text" type="text" placeholder="Enter text..." />
                
                <label for="textarea">Textarea:</label>
                <textarea id="textarea" placeholder="Enter multiple lines..."></textarea>
            </div>
        </section>
        
        <section>
            <h2>Links</h2>
            <p>
                This is a sample <a href="#">link to EPAM website</a> demonstrating the extracted 
                link color token from the theme.
            </p>
        </section>
        
        <footer>
            <p><strong>Theme Information</strong></p>
            <p>Token Source: <code>{metadata.source_url if metadata else 'Unknown'}</code></p>
            <p>Last Updated: <code>{metadata.extracted_at.isoformat() if metadata else 'Unknown'}</code></p>
            <p>Total Tokens: {len(tokens)} | 
               Extracted: {len(theme_config.get_extracted_tokens())} | 
               Unknown: {len(theme_config.get_unknown_tokens())}</p>
            <p style="font-size: 0.9rem; color: #999; margin-top: 2rem;">
                EPAM Theme Preview | Generated from ui/tokens/epam.tokens.json
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    return html


def _get_token_value(tokens, token_name: str, default: str = "not set") -> str:
    """Extract token value from tokens list."""
    for token in tokens:
        if token.name == token_name and token.status == TokenStatus.EXTRACTED:
            return str(token.value)
    return default


def _generate_styles_from_tokens(tokens) -> str:
    """Generate CSS styles from extracted tokens."""
    styles = []
    
    # Group tokens by element and build CSS
    elements = {}
    for token in tokens:
        if token.status != TokenStatus.EXTRACTED:
            continue
        
        # Parse token name to extract element and property
        parts = token.name.lower().split('-')
        if len(parts) < 2:
            continue
        
        element = parts[0]
        if element not in elements:
            elements[element] = {}
        
        # Map token properties to CSS
        prop_name = '-'.join(parts[1:])
        if prop_name == 'fontfamily':
            elements[element]['font-family'] = token.value
        elif prop_name == 'fontsize':
            elements[element]['font-size'] = token.value
        elif prop_name == 'fontweight':
            elements[element]['font-weight'] = token.value
        elif prop_name == 'lineheight':
            elements[element]['line-height'] = token.value
        elif prop_name == 'color':
            elements[element]['color'] = token.value
        elif prop_name == 'backgroundcolor':
            elements[element]['background-color'] = token.value
    
    # Generate CSS rules
    for element, properties in elements.items():
        if not properties:
            continue
        style_str = '; '.join(f"{k}: {v}" for k, v in properties.items())
        styles.append(f"{element} {{ {style_str}; }}")
    
    return '\n        '.join(styles) if styles else ""
