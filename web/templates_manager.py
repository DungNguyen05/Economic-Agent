# web/templates_manager.py - HTML templates for the web interface
import os
import logging
from pathlib import Path

import config

logger = logging.getLogger(__name__)

def create_templates() -> None:
    """Create HTML templates for the web interface if they don't exist"""
    # Check if the template directory exists
    templates_dir = Path(config.TEMPLATES_DIR)
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created templates directory: {templates_dir}")
    
    # Check if the index.html file exists
    index_path = templates_dir / "index.html"
    if not index_path.exists():
        logger.warning(f"Template file {index_path} not found. Please make sure it exists.")
    
    # Check if the static directory exists
    static_dir = Path(config.STATIC_DIR)
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created static directory: {static_dir}")
    
    # Check if the styles.css file exists
    css_path = static_dir / "styles.css"
    if not css_path.exists():
        logger.warning(f"CSS file {css_path} not found. Please make sure it exists.")
    
    logger.info("Template verification completed")