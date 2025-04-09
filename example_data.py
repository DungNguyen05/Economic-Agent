# example_data.py - Example economic data for initial setup
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def get_example_data() -> List[Dict]:
    """Return a list of example economic data documents"""
    return [
        {
            "content": "BTC(bitcoin) Price is 50$",
            "source": "BTC(bitcoin) Price is 50$"
        }
    ]

def load_example_data(document_manager) -> None:
    """Load example data into the document manager if it's empty"""
    # Only load if there are no documents
    if len(document_manager.documents) == 0:
        logger.info("Adding example economic data...")
        example_data = get_example_data()
        doc_ids = document_manager.bulk_add_documents(example_data)
        logger.info(f"Added {len(doc_ids)} example documents")
    else:
        logger.info("Document store already contains documents, skipping example data loading")