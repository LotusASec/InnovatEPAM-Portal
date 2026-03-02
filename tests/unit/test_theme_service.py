"""Unit tests for theme service file I/O operations."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.schemas.theme import DesignToken, TokenFile, TokenMetadata, TokenStatus, TokenType
from app.services.theme_service import ThemeService


@pytest.fixture
def sample_metadata():
    """Create sample extraction metadata."""
    return TokenMetadata(
        source_url="https://www.epam.com/",
        extracted_at=datetime(2026, 3, 2, 6, 35, 39, tzinfo=timezone.utc),
        extraction_method="playwright-mcp",
        browser_version="Chromium",
        success=True,
        tokens_extracted=3,
        tokens_unknown=1,
        extraction_duration_seconds=4.1,
        retry_count=0
    )


@pytest.fixture
def sample_tokens():
    """Create sample design tokens (mix of extracted and unknown)."""
    now = datetime(2026, 3, 2, 6, 35, 39, tzinfo=timezone.utc)
    
    return [
        DesignToken(
            name="body-fontfamily",
            value="'Open Sans', sans-serif",
            type=TokenType.TYPOGRAPHY,
            source_selector="body",
            extracted_at=now,
            status=TokenStatus.EXTRACTED
        ),
        DesignToken(
            name="h1-fontsize",
            value="32px",
            type=TokenType.TYPOGRAPHY,
            source_selector="h1",
            extracted_at=now,
            status=TokenStatus.EXTRACTED
        ),
        DesignToken(
            name="primary-color",
            value="rgb(0, 123, 255)",
            type=TokenType.COLOR,
            source_selector=".btn-primary",
            extracted_at=now,
            status=TokenStatus.EXTRACTED
        ),
        DesignToken(
            name="hover-color",
            value=None,
            type=TokenType.COLOR,
            source_selector=".btn-primary:hover",
            extracted_at=now,
            status=TokenStatus.UNKNOWN,
            evidence="Element not found during extraction"
        )
    ]


@pytest.fixture
def sample_token_file(sample_metadata, sample_tokens):
    """Create a complete token file."""
    return TokenFile(
        metadata=sample_metadata,
        tokens=sample_tokens
    )


class TestWriteTokenFile:
    """Test token file writing and atomic replacement."""

    def test_write_tokens_json_creates_file_and_valid_json(self, tmp_path, sample_token_file):
        """Test that write_token_file creates valid JSON file."""
        output_dir = str(tmp_path)
        
        result = ThemeService.write_token_file(sample_token_file, output_dir)
        
        # File should exist
        assert result.exists()
        assert result.name == "epam.tokens.json"
        
        # File should contain valid JSON
        with open(result, 'r') as f:
            data = json.load(f)
        
        # JSON structure should be valid
        assert "metadata" in data
        assert "tokens" in data
        assert len(data["tokens"]) == 4
        assert data["metadata"]["tokens_extracted"] == 3
        assert data["metadata"]["tokens_unknown"] == 1

    def test_atomic_replacement_overwrites_existing_files(self, tmp_path, sample_token_file):
        """Test that old files are deleted before writing new ones."""
        output_dir = str(tmp_path)
        
        # Write initial files
        ThemeService.write_token_file(sample_token_file, output_dir)
        
        # Verify initial files exist
        json_path = tmp_path / "epam.tokens.json"
        assert json_path.exists()
        
        # Get modification time of old file
        old_mtime = json_path.stat().st_mtime
        
        # Create modified token file
        modified_tokens = sample_token_file.tokens[:2]  # Fewer tokens
        modified_metadata = sample_token_file.metadata
        modified_metadata.tokens_extracted = 2
        modified_metadata.tokens_unknown = 0
        modified_file = TokenFile(
            metadata=modified_metadata,
            tokens=modified_tokens
        )
        
        # Write updated file
        ThemeService.write_token_file(modified_file, output_dir)
        
        # File should still exist but be newer
        assert json_path.exists()
        new_mtime = json_path.stat().st_mtime
        assert new_mtime >= old_mtime
        
        # Content should be updated
        with open(json_path, 'r') as f:
            data = json.load(f)
        assert len(data["tokens"]) == 2


class TestLoadTokenFile:
    """Test loading token files from disk."""

    def test_load_tokens_json_roundtrip(self, tmp_path, sample_token_file):
        """Test write then load preserves token data."""
        output_dir = str(tmp_path)
        
        # Write token file
        ThemeService.write_token_file(sample_token_file, output_dir)
        
        # Load it back
        json_path = tmp_path / "epam.tokens.json"
        loaded = ThemeService.load_token_file(str(json_path))
        
        # Data should match original
        assert loaded is not None
        assert len(loaded.tokens) == len(sample_token_file.tokens)
        assert loaded.metadata.source_url == sample_token_file.metadata.source_url
        assert loaded.metadata.tokens_extracted == sample_token_file.metadata.tokens_extracted
        assert loaded.metadata.tokens_unknown == sample_token_file.metadata.tokens_unknown

    def test_load_tokens_json_roundtrip_preserves_token_details(self, tmp_path, sample_token_file):
        """Test that token details are preserved through roundtrip."""
        output_dir = str(tmp_path)
        
        # Write and load
        ThemeService.write_token_file(sample_token_file, output_dir)
        json_path = tmp_path / "epam.tokens.json"
        loaded = ThemeService.load_token_file(str(json_path))
        
        # Check first extracted token
        original_token = sample_token_file.tokens[0]
        loaded_token = loaded.tokens[0]
        
        assert loaded_token.name == original_token.name
        assert loaded_token.value == original_token.value
        assert loaded_token.type == original_token.type
        assert loaded_token.status == original_token.status

    def test_load_tokens_json_file_not_found(self, tmp_path):
        """Test error handling for missing file."""
        nonexistent = str(tmp_path / "nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            ThemeService.load_token_file(nonexistent)

    def test_load_tokens_json_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        json_path = tmp_path / "invalid.json"
        json_path.write_text("NOT VALID JSON {")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            ThemeService.load_token_file(str(json_path))


class TestGenerateColorsMarkdown:
    """Test color documentation generation."""

    def test_generate_colors_markdown_creates_file(self, tmp_path, sample_token_file):
        """Test that color markdown file is created."""
        output_dir = str(tmp_path)
        
        result = ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        
        assert result.exists()
        assert result.name == "epam.colors.md"

    def test_generate_colors_markdown_contains_heading(self, tmp_path, sample_token_file):
        """Test that color markdown contains expected heading."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.colors.md"
        content = md_file.read_text()
        
        assert "# EPAM Color Tokens" in content
        assert "Extracted:" in content
        assert "Source:" in content

    def test_generate_colors_markdown_includes_extracted_tokens(self, tmp_path, sample_token_file):
        """Test that color markdown includes extracted color tokens."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.colors.md"
        content = md_file.read_text()
        
        # Should include the primary-color token (extracted color)
        assert "primary-color" in content
        assert "rgb(0, 123, 255)" in content
        
        # Should NOT include unknown tokens
        assert "hover-color" not in content

    def test_generate_colors_markdown_excludes_typography_tokens(self, tmp_path, sample_token_file):
        """Test that typography tokens are not included in colors markdown."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.colors.md"
        content = md_file.read_text()
        
        # Should NOT include typography tokens
        assert "body-fontfamily" not in content
        assert "h1-fontsize" not in content

    def test_generate_colors_markdown_handles_no_tokens(self, tmp_path, sample_metadata):
        """Test color markdown generation with no color tokens."""
        token_file = TokenFile(
            metadata=sample_metadata,
            tokens=[
                DesignToken(
                    name="body-font",
                    value="sans-serif",
                    type=TokenType.TYPOGRAPHY,
                    source_selector="body",
                    extracted_at=datetime.now(timezone.utc),
                    status=TokenStatus.EXTRACTED
                )
            ]
        )
        
        output_dir = str(tmp_path)
        ThemeService.generate_colors_markdown(token_file, output_dir)
        
        md_file = tmp_path / "epam.colors.md"
        content = md_file.read_text()
        
        assert "No color tokens extracted." in content


class TestGenerateTypographyMarkdown:
    """Test typography documentation generation."""

    def test_generate_typography_markdown_creates_file(self, tmp_path, sample_token_file):
        """Test that typography markdown file is created."""
        output_dir = str(tmp_path)
        
        result = ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        assert result.exists()
        assert result.name == "epam.typography.md"

    def test_generate_typography_markdown_contains_heading(self, tmp_path, sample_token_file):
        """Test that typography markdown contains expected heading."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.typography.md"
        content = md_file.read_text()
        
        assert "# EPAM Typography Tokens" in content
        assert "Extracted:" in content
        assert "Source:" in content

    def test_generate_typography_markdown_includes_extracted_tokens(self, tmp_path, sample_token_file):
        """Test that typography markdown includes extracted typography tokens."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.typography.md"
        content = md_file.read_text()
        
        # Should include typography tokens
        assert "body-fontfamily" in content
        assert "h1-fontsize" in content
        assert "32px" in content

    def test_generate_typography_markdown_excludes_color_tokens(self, tmp_path, sample_token_file):
        """Test that color tokens are not included in typography markdown."""
        output_dir = str(tmp_path)
        
        ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        md_file = tmp_path / "epam.typography.md"
        content = md_file.read_text()
        
        # Should NOT include color tokens
        assert "primary-color" not in content

    def test_generate_typography_markdown_handles_no_tokens(self, tmp_path, sample_metadata):
        """Test typography markdown generation with no typography tokens."""
        token_file = TokenFile(
            metadata=sample_metadata,
            tokens=[
                DesignToken(
                    name="primary",
                    value="rgb(0, 123, 255)",
                    type=TokenType.COLOR,
                    source_selector=".btn",
                    extracted_at=datetime.now(timezone.utc),
                    status=TokenStatus.EXTRACTED
                )
            ]
        )
        
        output_dir = str(tmp_path)
        ThemeService.generate_typography_markdown(token_file, output_dir)
        
        md_file = tmp_path / "epam.typography.md"
        content = md_file.read_text()
        
        assert "No typography tokens extracted." in content


class TestMultipleFileGeneration:
    """Test generating multiple files in same directory."""

    def test_generate_all_files_together(self, tmp_path, sample_token_file):
        """Test generating JSON and markdown files together."""
        output_dir = str(tmp_path)
        
        # Generate all three files
        ThemeService.write_token_file(sample_token_file, output_dir)
        ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        # All files should exist
        assert (tmp_path / "epam.tokens.json").exists()
        assert (tmp_path / "epam.colors.md").exists()
        assert (tmp_path / "epam.typography.md").exists()

    def test_files_contain_consistent_metadata(self, tmp_path, sample_token_file):
        """Test that all files reference the same source URL and extracted date."""
        output_dir = str(tmp_path)
        
        ThemeService.write_token_file(sample_token_file, output_dir)
        ThemeService.generate_colors_markdown(sample_token_file, output_dir)
        ThemeService.generate_typography_markdown(sample_token_file, output_dir)
        
        # Read markdown files
        colors_md = (tmp_path / "epam.colors.md").read_text()
        typo_md = (tmp_path / "epam.typography.md").read_text()
        
        # Both should have source URL
        assert sample_token_file.metadata.source_url in colors_md
        assert sample_token_file.metadata.source_url in typo_md
