# Automating ETL process with python
import pandas as pd
import logging

# Set-up the logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_the_data(file_path):
    """Extract the data"""
    try:
        df = pd.read_excel(file_path)
        logger.info("Data extracted successful.")
        return df
    except Exception as e:
        logger.error(f"Error while extracting data {e}")
        raise


def transofr_data(df):
    """Transform the data"""
    try:
        # First set in date time 
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['order_time'] = pd.to_datetime(df['order_time'], format="%H:%M:%S")
        
        # remove duplicates
        df = df.drop_duplicates()
        
        df = df.fillna({
            "quantity": 0,
            "unit_price": df["unit_price"].median()
        })
        
        # Add computed columns
        df["revenue"] = df["quantity"] * df["unit_price"]
        df["hour"] = df["order_time"].dt.hour
        df["minute"] = df["order_time"].dt.minute
        
        logger.info("Data transformed successful.")
        return df
    except Exception as e:
        logger.error(f"Error transforming data {e}")
        raise
    

def load_data(df, output_path):
    try:
        df.to_csv(output_path, index=False)
        logger.info("Data loadding is successful.")
    except Exception as e:
        logger.error(f"Error loading the data {e}")
        raise


def etl():
    try:
        input_path = "Data Model - Pizza Sales.csv"
        output_path = "transformed_data.csv"
        
        data = extract_the_data(input_path)
        data = transofr_data(data)
        load_data(data, output_path)
        
        logger.info("ETL process completed successfully")
    except Exception as e:
        logger.error(f"Error ETL process failed: {e}")
        raise
    

if __name__ == '__main__':
    etl()