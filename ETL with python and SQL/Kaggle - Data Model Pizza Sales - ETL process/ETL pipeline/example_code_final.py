# ========================== PROJECT STRUCTURE ==========================

# statista_pipeline/
# │
# ├── app.py                 # FastAPI endpoints
# ├── main.py                # Pipeline entry point
# ├── requirements.txt       # Required libraries
# ├── .env                   # Azure OpenAI credentials
# │
# ├── logs/
# │   └── pipeline.log       # Pipeline logs
# │
# ├── pipeline/
# │   ├── pipeline.py        # Main ETL/ELT orchestration
# │   ├── extractor.py       # API extraction logic
# │   ├── transformer.py     # pandas transformations
# │   ├── validators.py      # Data validation checks
# │   ├── loader.py          # SQLite loading logic
# │   ├── ai_enrichment.py   # Azure OpenAI + LangChain AI enrichment

# ========================== main.py ==========================

import logging
from pipeline.pipeline import StatistaPipeline

logging.basicConfig(filename="logs/pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") # Configure logging
if __name__ == "__main__":
    pipeline = StatistaPipeline() # Initialize pipeline
    pipeline.run() # Run ETL pipeline

# ========================== extractor.py ==========================

import requests
import pandas as pd
import logging
import time

logger = logging.getLogger(__name__)

class DataExtractor:
    URL = "https://jsonplaceholder.typicode.com/posts" # Public fake API
    def extract_data(self):
        logger.info("Starting API extraction")
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(self.URL, timeout=10) # API request
                response.raise_for_status() # Raise exception for bad status
                data = response.json() # JSON -> Python object
                logger.info(f"Extracted {len(data)} rows")
                df = pd.json_normalize(data) # JSON -> DataFrame
                return df

            except Exception as e:
                logger.error(f"API extraction failed: {e}")
                time.sleep(2)
        raise Exception("Extraction failed")


# ========================== validators.py ==========================

import logging
logger = logging.getLogger(__name__)

class DataValidator:
    REQUIRED_COLUMNS = ["userId", "id", "title", "body"] # Required schema

    def validate_schema(self, df):
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    
    def validate_empty(self, df):
        if df.empty:
            raise ValueError("Dataset is empty")

    def validate_duplicates(self, df):
        duplicates = df.duplicated().sum()
        logger.info(f"Duplicate rows: {duplicates}")


# ========================== transformer.py ==========================

import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataTransformer:

    def transform(self, df):
        logger.info("Starting transformation")
        df = df.drop_duplicates() # Remove duplicate rows
        df.columns = df.columns.str.lower().str.strip() # Clean column names
        df["title"] = df["title"].fillna("unknown") # Fill missing values
        df["title"] = df["title"].str.lower().str.strip() # Clean text
        df["title_length"] = df["title"].apply(len) # Feature engineering
        df["ingestion_time"] = datetime.now() # Add timestamp
        logger.info("Transformation complete")

        return df


# ========================== ai_enrichment.py ==========================

import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()

logger = logging.getLogger(__name__)

class AIEnrichmentService:

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_LLM_ENDPOINT"), # Azure endpoint
            api_key=os.getenv("AZURE_LLM_KEY"), # Azure key
            api_version=os.getenv("AZURE_LLM_VERSION_4"), # API version
            deployment_name=os.getenv("AZURE_LLM_GPT4oM"), # GPT deployment
            temperature=0
        )

    def generate_summary(self, text):
        prompt = f"Summarize this article in one short sentence:\n{text}" # LLM prompt
        response = self.llm.invoke([HumanMessage(content=prompt)]) # LLM request

        return response.content # Return AI response


# ========================== loader.py ==========================

import sqlite3
import logging

logger = logging.getLogger(__name__)

class DataLoader:

    DB_NAME = "statista.db"
    def load_sqlite(self, df):

        logger.info("Loading data into SQLite")
        conn = sqlite3.connect(self.DB_NAME) # DB connection
        df.to_sql("articles", conn, if_exists="replace", index=False) # DataFrame -> SQLite
        conn.close()
        logger.info("SQLite load complete")


# ========================== pipeline.py ==========================

import logging

from pipeline.extractor import DataExtractor
from pipeline.validators import DataValidator
from pipeline.transformer import DataTransformer
from pipeline.loader import DataLoader
from pipeline.ai_enrichment import AIEnrichmentService

logger = logging.getLogger(__name__)

class StatistaPipeline:

    def __init__(self):

        self.extractor = DataExtractor()
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.ai_service = AIEnrichmentService()

    def run(self):

        try:
            logger.info("Pipeline started")
            df = self.extractor.extract_data() # Extract
            self.validator.validate_schema(df) # Validate schema
            self.validator.validate_empty(df) # Validate empty data
            self.validator.validate_duplicates(df) # Validate duplicates
            df = self.transformer.transform(df) # Transform
            logger.info("Generating AI summaries")
            df["ai_summary"] = df["body"].apply(self.ai_service.generate_summary) # AI enrichment
            self.loader.load_sqlite(df) # Load to DB
            logger.info("Pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


# ========================== app.py ==========================

from fastapi import FastAPI
import sqlite3
import pandas as pd

app = FastAPI(title="Statista AI Pipeline")

@app.get("/health")
def health():
    return {"status": "running"} # Health check endpoint

@app.get("/articles")
def get_articles():
    conn = sqlite3.connect("statista.db") # DB connection
    query = "SELECT * FROM articles LIMIT 20"
    df = pd.read_sql(query, conn) # Read SQL table
    conn.close()

    return df.to_dict(orient="records") # Return JSON response