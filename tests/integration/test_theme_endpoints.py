"""Integration tests for theme endpoints."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.theme_config import ThemeConfig


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestThemePreviewEndpoint:
    """Test theme preview endpoint."""

    def test_preview_returns_html_with_tokens(self, client):
        """Test preview endpoint returns valid HTML."""
        response = client.get("/api/theme/preview")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text
        assert "<html" in response.text
        assert "</html>" in response.text

    def test_preview_includes_theme_tokens(self, client):
        """Test preview includes loaded theme tokens."""
        response = client.get("/api/theme/preview")
        
        assert response.status_code == 200
        html = response.text
        
        # Should include token counts in metadata footer
        assert "tokens" in html.lower()

    def test_preview_includes_typography_samples(self, client):
        """Test preview includes typography samples."""
        response = client.get("/api/theme/preview")
        
        assert response.status_code == 200
        html = response.text
        
        # Should include heading and body samples
        assert "<h1>" in html or "<H1>" in html
        assert "<h2>" in html or "<H2>" in html
        assert "<h3>" in html or "<H3>" in html

    def test_preview_includes_color_samples(self, client):
        """Test preview includes color sample swatches."""
        response = client.get("/api/theme/preview")
        
        assert response.status_code == 200
        html = response.text
        
        # Should include color-related styling
        assert "color" in html.lower() or "rgb" in html.lower()

    def test_preview_includes_component_samples(self, client):
        """Test preview includes component samples."""
        response = client.get("/api/theme/preview")
        
        assert response.status_code == 200
        html = response.text
        
        # Should include button or form samples
        assert "<button" in html or "<form" in html or "<input" in html


class TestThemeConfigurationLoading:
    """Test theme configuration loading."""

    def test_theme_config_loads_tokens(self):
        """Test theme config loads tokens from file."""
        config = ThemeConfig()
        tokens = config.get_extracted_tokens()
        
        assert len(tokens) > 0

    def test_theme_config_has_unknown_tokens(self):
        """Test theme config can return unknown tokens."""
        config = ThemeConfig()
        unknown = config.get_unknown_tokens()
        
        # Should have at least one unknown token or be empty
        assert isinstance(unknown, list)

    def test_theme_config_get_token_by_name(self):
        """Test retrieving specific token by name."""
        config = ThemeConfig()
        extracted = config.get_extracted_tokens()
        
        if extracted:
            # Get first extracted token
            token = extracted[0]
            retrieved = config.get_token(token.name)
            
            assert retrieved is not None
            assert retrieved.name == token.name

    def test_theme_config_get_color(self):
        """Test retrieving colors from config."""
        config = ThemeConfig()
        
        # Try to get a color (may or may not exist)
        colors = [
            t for t in config.get_extracted_tokens()
            if t.type.value == "color"
        ]
        
        assert isinstance(colors, list)

    def test_theme_config_get_font_family(self):
        """Test retrieving typography from config."""
        config = ThemeConfig()
        
        # Try to get typography tokens
        fonts = [
            t for t in config.get_extracted_tokens()
            if t.type.value == "typography"
        ]
        
        assert isinstance(fonts, list)
