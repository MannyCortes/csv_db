# handles python logic formatting, checking for empty cells
import logging
import pandas as pd
import pandas.errors as pd_err 
import puremagic 
from datatime import datetime
#configure the logger and file directory and what information to Log
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

file_path = r"C:\Users\manny\OneDrive\Desktop\pdf_db\practice.csv"
chunk_size = 10000

def file_type_check(file_path):
    try:
        file_type = puremagic.from_file(file_path)
        #if headers are missing, pure returns txt
        if file_type in [".csv", ".txt"]: 
            logger.info("File type check successful for file: %s, file type: %s", file_path, file_type)
            return True
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
        #if needed we can also chunk our pd.read_csv to manage memory for large csv files, but for now we will read the whole file at once
        usecols = ["Transaction_ID", "Date", "Customer_Name", "Item_Purchased", "Quantity", "Unit_Price", "Total_Amount", "Status"]
        csv_data = pd.read_csv(file_path, usecols=usecols)
        csv_data = csv_data.where(pd.notnull(csv_data), None)
        #tells pandas to keep all cells that are notnull if it is null replace to None 
        csv_dict = csv_data.to_dict(orient="records")
        logger.info("CSV data processed successfully for file: %s", file_path)
        #turns csv_dict into a list of dicts 
        clean_list = csv_df_check(csv_dict)
        #read_csv automatically manages iterating row ids, we can ovverried thisusing index_col="id"
        # if no header in csv file use names parameter'
    except UnicodeDecodeError: 
        logger.error("File encoding is not supported for: %s", file_path)
        decode_csv(file_path)
    except pd_err.ParserError:  logger.error("Parsing error for file: %s, check the csv format and delimiters", file_path)
    except FileNotFoundError:   logger.error("File not found for file: %s", file_path)
    except ValueError:  logger.error("Invalid parameters for reading CSV file: %s", file_path)
    except Exception as e: logger.error("An error occurred while processing CSV file: %s, error: %s", file_path, e)

def csv_df_check(df):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_list = []
    error_list = []
    #None is caught since we replaced missing values with None
    for row in df:
        if row.get("Transaction_ID") is None: 
            row["Error"] = "Missing Transaction_ID"
            row["Timestamp"] = time 
            error_list.append(row) 
            continue
        if row.get("Date") is None:
            row["Error"] = "Missing Date"
            row["Timestamp"] = time
            error_list.append(row)
            continue
        if row.get("Total_Amount") is None:
            row["Error"] = "Missing Total_Amount"
            row["Timestamp"] = time
            error_list.append(row)
            continue
        try:    row["Total_Amount"] = float(row["Total_Amount"]) 
        except (ValueError, TypeError):
            row["Error"] = "Invalid Total_Amount"
            row["Timestamp"] = time
            error_list.append(row) 
            continue
        try:  row["Quantity"] = int(row["Quantity"])
        except (ValueError, TypeError):
            row["Error"] = "Invalid Quantity"
            row["Timestamp"] = time
            error_list.append(row)
            continue
        clean_list.append(row)
        if len(error_list) > 0:
            bad_df = pd.DataFrame(error_list)
            #pd automitcally creates our headers using dict keys

            bad_df.to_csv(f"bad_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            #creates a csv file with the bad data
            logger.warning("Data quality issues found in file: %s, %d rows with errors. See bad_data_%s.csv for details.", file_path, len(error_list), datetime.now().strftime('%Y%m%d_%H%M%S'))
    return clean_list

def decode_csv(file_path): 
    pass

def main():
    # example  
    if file_type_check(file_path):
        clean_data = process_csv(file_path)
        
if __name__ == "__main__":    main()