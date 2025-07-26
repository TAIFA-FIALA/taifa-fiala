"""
Test Script for AI Africa Funding Tracker File Ingestion Pipeline
================================================================

This script tests the functionality of the file ingestion pipeline by:
1. Creating test files (PDF, CSV, text)
2. Processing them using the file processors
3. Verifying the extracted data
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
sys.path.append(parent_dir)

from data_processors.src.taifa_etl.services.file_ingestion.processors.pdf_processor import PDFProcessor
from data_processors.src.taifa_etl.services.file_ingestion.processors.csv_processor import CSVProcessor
from data_processors.src.taifa_etl.services.file_ingestion.processors.text_processor import TextProcessor
from data_processors.src.taifa_etl.services.file_ingestion.processors.url_processor import URLProcessor
from data_processors.src.taifa_etl.services.file_ingestion.deduplication.deduplicator import FundingDeduplicator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileIngestionTester:
    """
    Tester for the file ingestion pipeline.
    """
    
    def __init__(self):
        """Initialize the tester."""
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize processors
        self.pdf_processor = PDFProcessor()
        self.csv_processor = CSVProcessor()
        self.text_processor = TextProcessor()
        self.url_processor = URLProcessor()
        
        # Initialize deduplicator
        self.deduplicator = FundingDeduplicator()
        
    def cleanup(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)
        
    async def run_tests(self):
        """Run all tests."""
        try:
            await self.test_pdf_processor()
            await self.test_csv_processor()
            await self.test_text_processor()
            await self.test_deduplication()
            
            self.logger.info("All tests completed successfully!")
            
        except Exception as e:
            self.logger.error(f"Test failed: {e}")
            raise
        finally:
            self.cleanup()
    
    async def test_pdf_processor(self):
        """Test the PDF processor."""
        self.logger.info("Testing PDF processor...")
        
        # Create a test PDF file
        pdf_path = self._create_test_pdf()
        
        # Process the PDF
        result = await self.pdf_processor.process(pdf_path)
        
        # Verify the result
        self._verify_processor_result(result, 'pdf')
        
        self.logger.info("PDF processor test passed!")
    
    async def test_csv_processor(self):
        """Test the CSV processor."""
        self.logger.info("Testing CSV processor...")
        
        # Create a test CSV file
        csv_path = self._create_test_csv()
        
        # Process the CSV
        result = await self.csv_processor.process(csv_path)
        
        # Verify the result
        self._verify_processor_result(result, 'csv')
        
        self.logger.info("CSV processor test passed!")
    
    async def test_text_processor(self):
        """Test the text processor."""
        self.logger.info("Testing text processor...")
        
        # Create a test text file
        text_path = self._create_test_text()
        
        # Process the text
        result = await self.text_processor.process(text_path)
        
        # Verify the result
        self._verify_processor_result(result, 'text')
        
        self.logger.info("Text processor test passed!")
    
    async def test_deduplication(self):
        """Test the deduplication logic."""
        self.logger.info("Testing deduplication...")
        
        # Create test records
        records = self._create_test_records()
        
        # Add duplicate records
        duplicates = self._create_duplicate_records(records)
        all_records = records + duplicates
        
        # Check for duplicates
        unique_records, duplicate_records = await self.deduplicator.check_duplicates(all_records)
        
        # Verify the result
        assert len(unique_records) == len(records), f"Expected {len(records)} unique records, got {len(unique_records)}"
        assert len(duplicate_records) == len(duplicates), f"Expected {len(duplicates)} duplicate records, got {len(duplicate_records)}"
        
        self.logger.info("Deduplication test passed!")
    
    def _create_test_pdf(self) -> Path:
        """
        Create a test PDF file.
        
        Returns:
            Path to the test PDF file
        """
        # Since we can't easily create a PDF file programmatically,
        # we'll create a text file with a .pdf extension for testing
        pdf_path = Path(self.temp_dir) / "test.pdf"
        
        with open(pdf_path, 'w') as f:
            f.write("This is a test PDF file.\n\n")
            f.write("Acme AI Corp received $10 million in Series A funding on January 15, 2023.\n")
            f.write("The round was led by Tech Ventures with participation from AI Capital.\n")
            f.write("The funding will be used to develop new AI models for healthcare applications in Africa.\n")
        
        return pdf_path
    
    def _create_test_csv(self) -> Path:
        """
        Create a test CSV file.
        
        Returns:
            Path to the test CSV file
        """
        csv_path = Path(self.temp_dir) / "test.csv"
        
        with open(csv_path, 'w') as f:
            f.write("company_name,funding_amount,funding_date,funding_round,lead_investor,sector\n")
            f.write("Acme AI Corp,$10M,2023-01-15,Series A,Tech Ventures,Healthcare\n")
            f.write("Data Analytics Nigeria,$5M,2023-02-20,Seed,Africa Ventures,Data Analytics\n")
            f.write("ML Solutions Kenya,$2.5M,2023-03-10,Pre-seed,Kenya Angels,Machine Learning\n")
        
        return csv_path
    
    def _create_test_text(self) -> Path:
        """
        Create a test text file.
        
        Returns:
            Path to the test text file
        """
        text_path = Path(self.temp_dir) / "test.txt"
        
        with open(text_path, 'w') as f:
            f.write("AI Funding News\n\n")
            f.write("Acme AI Corp has secured $10 million in Series A funding.\n")
            f.write("The round was led by Tech Ventures with participation from AI Capital.\n")
            f.write("The funding will be used to develop new AI models for healthcare applications in Africa.\n\n")
            f.write("In other news, Data Analytics Nigeria raised $5 million in seed funding from Africa Ventures.\n")
        
        return text_path
    
    def _create_test_records(self) -> list:
        """
        Create test records for deduplication testing.
        
        Returns:
            List of test records
        """
        return [
            {
                'organization_name': 'Acme AI Corp',
                'amount_usd': 10000000,
                'transaction_date': '2023-01-15',
                'funding_stage': 'Series A',
                'lead_investor_name': 'Tech Ventures',
                'ai_sectors': ['Healthcare'],
                'geographic_focus': ['Africa'],
                'source_type': 'test'
            },
            {
                'organization_name': 'Data Analytics Nigeria',
                'amount_usd': 5000000,
                'transaction_date': '2023-02-20',
                'funding_stage': 'Seed',
                'lead_investor_name': 'Africa Ventures',
                'ai_sectors': ['Data Analytics'],
                'geographic_focus': ['Nigeria'],
                'source_type': 'test'
            },
            {
                'organization_name': 'ML Solutions Kenya',
                'amount_usd': 2500000,
                'transaction_date': '2023-03-10',
                'funding_stage': 'Pre-seed',
                'lead_investor_name': 'Kenya Angels',
                'ai_sectors': ['Machine Learning'],
                'geographic_focus': ['Kenya'],
                'source_type': 'test'
            }
        ]
    
    def _create_duplicate_records(self, records: list) -> list:
        """
        Create duplicate records with slight variations.
        
        Args:
            records: Original records
            
        Returns:
            List of duplicate records
        """
        duplicates = []
        
        for record in records:
            # Create a duplicate with slight variations
            duplicate = record.copy()
            duplicate['source_type'] = 'duplicate_test'
            
            # Vary the organization name slightly
            duplicate['organization_name'] = record['organization_name'].upper()
            
            # Vary the amount slightly
            duplicate['amount_usd'] = record['amount_usd'] * 1.01
            
            duplicates.append(duplicate)
        
        return duplicates
    
    def _verify_processor_result(self, result: dict, expected_source_type: str):
        """
        Verify the result of a processor.
        
        Args:
            result: Processor result
            expected_source_type: Expected source type
        """
        assert 'records' in result, "Result should contain 'records'"
        assert 'source_type' in result, "Result should contain 'source_type'"
        assert 'metadata' in result, "Result should contain 'metadata'"
        
        assert result['source_type'] == expected_source_type, f"Expected source_type '{expected_source_type}', got '{result['source_type']}'"
        assert len(result['records']) > 0, "Expected at least one record"
        
        # Verify record structure
        for record in result['records']:
            assert 'extraction_method' in record, "Record should contain 'extraction_method'"
            
            # At least one of these fields should be present
            assert any(field in record for field in ['organization_name', 'amount_usd']), "Record should contain at least one key field"


async def main():
    """Main entry point for the test script."""
    tester = FileIngestionTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())