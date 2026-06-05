# handles python logic formatting, checking for empty cells
import logging
import pandas as pd
import pandas.errors as pd_err 
import puremagic 
#configure the logger and file directory and what information to Log
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

chunk_size = 10000

def file_type_check(file_path):
    try:
        file_type = puremagic.from_file(file_path)
        if file_type == ".csv": process_csv(file_path)
        logger.info("File type check successful for file: %s, file type: %s", file_path, file_type)
    except FileNotFoundError:
        logger.error("File not found for file: %s", file_path)
    except puremagic.PureValueError:
        logger.warning("File is empty: %s", file_path)
    except puremagic.PureError:
        logger.error("Could not determine file type for: %s", file_path)
    except Exception as e:
        logger.error("An error occurred: %s", e)

def process_csv(file_path):
    try:
        #if no header use the names parameter to provide column names, if header is present use header=0 to read the first row as column names
        #use_coles is a param for pandas to read, contains our column names
        usecols = ["Transaction_ID", "Date", "Customer_Name", "Item_Purchased", "Quantity", "Unit_Price", "Total_Amount", "Status"]
        #if needed we can also chunk our pd.read_csv to manage memory for large csv files, but for now we will read the whole file at once
        csv_data = pd.read_csv(file_path, usecols=usecols)
        csv_data = csv_data.where(pd.notnull(csv_data), None)
        #tells pandas to keep all cells that are notnull if it is null replace to None 
        csv_dict = csv_data.to_dict(orient="records")
        #turns csv_dict into a list of dicts 
        print(csv_dict)
        #read_csv automatically manages iterating row ids, we can ovverried thisusing index_col="id"
        # if no header in csv file use names parameter'
    except UnicodeDecodeError: 
        print(f"File encoding is not supported for: {file_path}")
        decode_csv(file_path)
    except pd_err.ParserError:  logger.error("Parsing error for file: %s, check the csv format and delimiters", file_path)
    except FileNotFoundError:   logger.error("File not found for file: %s", file_path)
    except ValueError:  logger.error("Invalid parameters for reading CSV file: %s", file_path)

def decode_csv(file_path): 
    pass

def main():
    # example  
    file_path = r"C:\Users\manny\OneDrive\Desktop\pdf_db\practice.csv"
    file_type_check(file_path)
if __name__ == "__main__":    main()