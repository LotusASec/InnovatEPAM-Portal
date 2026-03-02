#!/usr/bin/env python3
"""
CLI script for extracting EPAM design tokens using MCP/Playwright automation.

Usage:
    python scripts/extract_epam_tokens.py [--url URL] [--output-dir DIR] [--verbose] [--help]

Exit codes:
    0: Success - tokens extracted
    1: Partial Failure - some tokens extracted, some marked unknown
    2: Total Failure - zero tokens extracted
    3: Configuration Error - invalid arguments or missing dependencies
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.theme_extraction_service import ThemeExtractionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for CLI script."""
    parser = argparse.ArgumentParser(
        description='Extract EPAM design tokens using Playwright automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/extract_epam_tokens.py
  python scripts/extract_epam_tokens.py --url https://www.epam.com/ --output-dir ui/tokens/
  python scripts/extract_epam_tokens.py --verbose
        '''
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default='https://www.epam.com/',
        help='Source website URL (default: https://www.epam.com/)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='ui/tokens/',
        help='Output directory for token files (default: ui/tokens/)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        logger.error(f"Configuration Error: Invalid URL format: {args.url}")
        return 3
    
    # Validate output directory
    try:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_path.absolute()}")
    except (OSError, PermissionError) as e:
        logger.error(f"Configuration Error: Cannot create output directory: {e}")
        return 3
    
    # Run extraction
    logger.info(f"Extracting tokens from: {args.url}")
    logger.info(f"Output directory: {args.output_dir}")
    
    try:
        # Create extraction service
        service = ThemeExtractionService(url=args.url)
        
        # Run async extraction
        token_file = await service.extract_tokens()
        
        # Write to files
        await service.write_tokens_to_file(token_file, args.output_dir)
        service.generate_colors_markdown(token_file.tokens, args.output_dir)
        service.generate_typography_markdown(token_file.tokens, args.output_dir)
        
        # Log summary
        logger.info(f"✓ Extraction Complete")
        logger.info(f"  Total tokens: {len(token_file.tokens)}")
        logger.info(f"  Extracted: {token_file.metadata.tokens_extracted}")
        logger.info(f"  Unknown: {token_file.metadata.tokens_unknown}")
        logger.info(f"  Duration: {token_file.metadata.extraction_duration_seconds:.1f}s")
        
        # Determine exit code based on extraction results
        if token_file.metadata.success:
            if token_file.metadata.tokens_unknown > 0:
                logger.warning("Partial extraction: Some tokens marked as unknown")
                return 1  # Partial success
            else:
                return 0  # Full success
        else:
            logger.error("Total failure: No tokens extracted")
            return 2
    
    except KeyboardInterrupt:
        logger.warning("Extraction interrupted by user")
        return 2
    
    except Exception as e:
        logger.error(f"Total Failure: {type(e).__name__}: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

