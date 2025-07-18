import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

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


def main():
    # Configure the Gemini API
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Read the markdown content
    try:
        with open(os.path.join(os.getcwd(), "grantsdatabase_africa.md"), "r", encoding="utf-8") as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("Error: grantsdatabase_africa.md not found. Please run the crawler first.")
        return

    # Manually construct a simplified schema for AfricaIntelligenceItem
    # This is to avoid issues with the full Pydantic JSON schema output
    intelligence_item_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "amount": {"type": "string"},
                "currency": {"type": "string"},
                "deadline": {"type": "string"},
                "source_url": {"type": "string"},
                "geographical_scope": {"type": "string"},
                "eligibility_criteria": {"type": "string"}
            },
            "required": ["title"] # Assuming title is always required
        }
    }

    # Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": intelligence_item_schema, # Pass the simplified schema
        },
    )

    # Create the prompt
    prompt_text = f"""Extract ALL intelligence feed from the following markdown content into a JSON array. Each object in the array should conform to the AfricaIntelligenceItem schema. Ensure all fields are extracted accurately. If a field is not present, set it to null. The source_url should be the direct link to the intelligence item, not the category page. The geographical_scope should be 'Africa' unless specified otherwise. The eligibility_criteria should be extracted from the description if available.\n\n{markdown_content}"""

    # Generate content
    try:
        response = model.generate_content(prompt_text)

        # Access the parsed structured data
        if response.text:
            extracted_data = json.loads(response.text)
            # Save to JSON
            with open("africa_intelligence_feed.json", "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=4)
            print("Extracted data saved to africa_intelligence_feed.json")
        else:
            print("No data extracted from Gemini API.")
            print(f"Raw response: {response}")

    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        main()