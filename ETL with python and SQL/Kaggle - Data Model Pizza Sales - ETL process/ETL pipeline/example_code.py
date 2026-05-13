# ========================= main.py =========================

import logging # logging framework
from pipeline.pipeline import PizzaPipeline # ETL orchestrator class

logging.basicConfig(level=logging.INFO) # configure logging level

if __name__ == "__main__":
    pipeline = PizzaPipeline(input_path="data/raw/pizza_sales.csv") # initialize pipeline
    pipeline.run() # execute complete ETL pipeline

# ========================= pipeline.py =========================

import pandas as pd, sqlite3, logging, dlt # ETL + DB + automated ingestion
from pipeline.validators import DataValidator # validation service
from pipeline.ai_enrichment import AIEnrichmentService # AI enrichment layer

logger = logging.getLogger(__name__) # logger object


class PizzaPipeline:

    def __init__(self, input_path:str, db_name:str="sales.db"):
        self.input_path = input_path # raw source file
        self.db_name = db_name # SQLite DB name
        self.df = None # dataframe placeholder

    # ------------------------- EXTRACT -------------------------

    def extract(self):
        logger.info(f"Extracting data from {self.input_path}") # extraction log
        self.df = pd.read_csv(self.input_path) # ingest raw CSV
        logger.info(f"Extracted {len(self.df)} rows") # row count monitoring

    # ------------------------- VALIDATE -------------------------

    def validate(self):
        logger.info("Validating dataset") # validation started
        validator = DataValidator() # create validator object
        validator.validate_required_columns(self.df) # schema validation
        validator.validate_quantity(self.df) # business rule validation
        logger.info("Validation complete") # validation finished

    # ------------------------- TRANSFORM -------------------------

    def transform(self):
        logger.info("Starting transformations") # transformation started
        self.df = self.df.drop_duplicates() # remove duplicate rows
        self.df["quantity"] = self.df["quantity"].fillna(0) # replace null quantity with 0
        self.df["unit_price"] = self.df["unit_price"].fillna(self.df["unit_price"].median()) # median imputation
        self.df["order_date"] = pd.to_datetime(self.df["order_date"]) # convert order_date to datetime
        self.df["order_time"] = pd.to_datetime(self.df["order_time"]) # convert order_time to datetime
        self.df["revenue"] = self.df["quantity"] * self.df["unit_price"] # feature engineering for revenue
        self.df["hour"] = self.df["order_time"].dt.hour # extract hour from order_time
        self.df["minute"] = self.df["order_time"].dt.minute # extract minute from order_time
        self.df["day_name"] = self.df["order_date"].dt.day_name() # extract weekday name
        logger.info("Transformation complete") # transformation finished

    # ------------------------- AI ENRICHMENT -------------------------

    def generate_ai_summary(self):
        logger.info("Generating AI insights") # AI enrichment started
        ai_service = AIEnrichmentService() # initialize AI service
        summary = ai_service.generate_summary(self.df) # generate AI summary
        print("\n===== AI GENERATED INSIGHTS =====\n") # output header
        print(summary) # print AI insights

    # ------------------------- SQLITE LOAD -------------------------

    def load_sqlite(self):
        logger.info("Loading data into SQLite") # SQLite loading started
        conn = sqlite3.connect(self.db_name) # DB connection
        self.df.to_sql("pizza_sales", conn, if_exists="replace", index=False) # load dataframe into SQLite
        conn.close() # close connection
        logger.info("SQLite load complete") # load success

    # ------------------------- DLT LOAD -------------------------

    def load_dlt(self):
        logger.info("Loading data with dlt") # dlt automated ingestion
        pipeline = dlt.pipeline(pipeline_name="pizza_pipeline", destination="duckdb", dataset_name="pizza_data") # initialize dlt pipeline
        load_info = pipeline.run(self.df, table_name="sales") # automated schema + load
        logger.info(load_info) # pipeline metadata logs

    # ------------------------- RUN PIPELINE -------------------------

    def run(self):
        self.extract() # ingestion layer
        self.validate() # validation layer
        self.transform() # transformation layer
        self.generate_ai_summary() # AI automation layer
        self.load_sqlite() # SQLite warehouse load
        self.load_dlt() # automated dlt ingestion
        logger.info("Pipeline execution completed") # pipeline finished
        

# ========================= validators.py =========================

class DataValidator:

    REQUIRED_COLUMNS = ["order_id","quantity","unit_price"] # expected schema definition

    def validate_required_columns(self, df):
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns] # detect schema mismatch
        if missing:
            raise ValueError(f"Missing columns: {missing}") # stop pipeline if schema invalid

    def validate_quantity(self, df):
        if (df["quantity"] < 0).any(): # detect invalid negative quantity
            raise ValueError("Negative quantity detected") # fail validation


# ========================= ai_enrichment.py =========================

import os # environment variables
from dotenv import load_dotenv # load .env file
from openai import AzureOpenAI # Azure OpenAI SDK

load_dotenv() # initialize env variables


class AIEnrichmentService:

    def __init__(self):
        self.client = AzureOpenAI(api_key=os.getenv("AZURE_LLM_KEY"), api_version=os.getenv("AZURE_LLM_VERSION_4"), azure_endpoint=os.getenv("AZURE_LLM_ENDPOINT")) # Azure OpenAI client
        self.model = os.getenv("AZURE_LLM_GPT4oM") # deployment/model name

    def generate_summary(self, df):
        sample = df.head(5).to_string() # convert sample rows to text
        prompt = f"""
        Analyze this sales dataset and generate:
        1. Business insights
        2. Data quality observations
        3. Suggested KPIs
        4. Potential anomalies

        Dataset:
        {sample}
        """
        response = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=0.2) # AI request
        return response.choices[0].message.content # return AI insights


# ========================= app.py =========================

from fastapi import FastAPI # API framework
import sqlite3, pandas as pd # DB + dataframe libraries

app = FastAPI() # initialize API application


@app.get("/sales") # REST API endpoint
def get_sales():
    conn = sqlite3.connect("sales.db") # connect SQLite database
    df = pd.read_sql("SELECT * FROM pizza_sales LIMIT 20", conn) # query analytical table
    conn.close() # close DB connection
    return df.to_dict(orient="records") # return JSON response