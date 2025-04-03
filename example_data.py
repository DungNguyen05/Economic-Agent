# example_data.py - Example economic data for initial setup
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def get_example_data() -> List[Dict]:
    """Return a list of example economic data documents"""
    return [
        {
            "content": "The Federal Reserve raised interest rates by 0.25% in September 2023, bringing the federal funds rate to 5.25-5.50%. This was the 11th rate hike since March 2022 as part of the Fed's effort to combat inflation.",
            "source": "Federal Reserve Press Release, September 2023"
        },
        {
            "content": "US GDP grew at an annual rate of 2.1% in Q2 2023, showing resilience despite high interest rates. Consumer spending, which accounts for more than two-thirds of U.S. economic activity, increased at a 1.7% rate.",
            "source": "Bureau of Economic Analysis, Q2 2023 Report"
        },
        {
            "content": "The Consumer Price Index (CPI) increased 3.7% for the 12 months ending September 2023, before seasonal adjustment. The index for all items less food and energy rose 4.1% over the last 12 months.",
            "source": "Bureau of Labor Statistics, CPI Report October 2023"
        },
        {
            "content": "The US unemployment rate stood at 3.8% in September 2023, reflecting a historically tight labor market. The economy added 336,000 jobs in September, significantly exceeding economists' expectations.",
            "source": "Bureau of Labor Statistics, Employment Report October 2023"
        },
        {
            "content": "The S&P 500 index reached 4,308 at the end of September 2023, representing a 13% increase from the beginning of the year. However, market volatility increased due to concerns about interest rates and inflation.",
            "source": "Market Summary, Q3 2023"
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