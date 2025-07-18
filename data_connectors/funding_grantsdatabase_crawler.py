
import json
import asyncio
import os
from pydantic import BaseModel, Field
from typing import List, Optional

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from dotenv import load_dotenv

load_dotenv()

# Define the Pydantic model for the extracted data, based on the database schema
class AfricaIntelligenceItem(BaseModel):
    title: str = Field(..., description="The title of the intelligence item.")
    description: Optional[str] = Field(None, description="A brief description of the intelligence item.")
    amount: Optional[str] = Field(None, description="The amount of funding available.")
    currency: Optional[str] = Field(None, description="The currency of the funding amount.")
    deadline: Optional[str] = Field(None, description="The application deadline.")
    source_url: Optional[str] = Field(None, description="The URL to the original intelligence item page.")
    geographical_scope: Optional[str] = Field(None, description="The geographical scope of the intelligence item.")
    eligibility_criteria: Optional[str] = Field(None, description="The eligibility criteria for applicants.")

class FundingData(BaseModel):
    data: List[AfricaIntelligenceItem] = Field(..., description="A list of intelligence feed.")

async def main():
    # URL to crawl
    url = "https://grantsdatabase.org/category/africa/"

    # Define the crawler run configuration (without LLM extraction for now)
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
    )

    # Initialize the crawler and run it
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

    # Save the raw markdown content
    if result and result.markdown:
        with open("grantsdatabase_africa.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print("Raw markdown content saved to grantsdatabase_africa.md")
    else:
        print("No markdown content extracted.")

if __name__ == "__main__":
    asyncio.run(main())
