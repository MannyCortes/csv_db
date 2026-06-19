# handles python logic formatting, checking for empty cells
import logging
import pandas as pd
import pandas.errors as pd_err 
import chardet
import re
from datetime import datetime
#configure the logger and file directory and what information to Log
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def file_type_check(file, filename):
    try:
        
        #if headers are missing, pure returns txt
        header = file.read(2048)
        #read the first few bytes
        filename = filename.lower() 
        #csv and txt are placed in a typle
        if filename.endswith((".csv", ".txt")): 
            file.seek(0)
            logger.info("File type check successful for file: %s, file type: %s", filename)
            return True
    except FileNotFoundError:
        logger.error("File not found for file: %s", filename)
    except Exception as e:
        logger.error("An error occurred: %s", e)

def process_csv(file, filename):
    '''Reads a CSV file, checks for data quality issues, and returns a list of clean records.
    If data quality issues are found, they are logged and the bad records are saved to a separate CSV file for review.'''
    try:
        #if no header use the names parameter to provide column names, if header is present use header=0 to read the first row as column names
        #use_coles is a param for pandas to read, contains our column names
        #if needed we can also chunk our pd.read_csv to manage memory for large csv files, but for now we will read the whole file at once
        usecols = ["Transaction_ID", "Date", "Customer_Name", "Item_Purchased", "Quantity", "Unit_Price", "Total_Amount", "Status"]
        csv_data = pd.read_csv(file, usecols=usecols)
        csv_data = csv_data.where(pd.notnull(csv_data), None)
        #tells pandas to keep all cells that are notnull if it is null replace to None 
        csv_dict = csv_data.to_dict(orient="records")
        logger.info("CSV data processed successfully for file")
        #turns csv_dict into a list of dicts 
        clean_list = csv_df_check(csv_dict) 
        if clean_list: return clean_list 
        else: return None
        #read_csv automatically manages iterating row ids, we can ovverried thisusing index_col="id"
        # if no header in csv file use names parameter'
    except UnicodeDecodeError: 
        logger.info("Error Decoding File")
        #reset cursor
        file.seek(0)
        csv_dict = decode_csv(file, filename)
        clean_list = csv_df_check(csv_dict)
        if clean_list: return clean_list
        else: return None 
    except pd_err.ParserError:  logger.error("Parsing error for file: %s, check the csv format and delimiters", filename)
    except FileNotFoundError:   logger.error("File not found for file: %s", filename)
    except ValueError:  logger.error("Invalid parameters for reading CSV file: %s", filename)
    except Exception as e: logger.error("An error occurred while processing CSV file: %s, error: %s", filename, e)

def csv_df_check(df):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_list = []
    error_list = []
    #None is caught since we replaced missing values with None
    r_date = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    r_int = re.compile(r"^\d+$")
    r_float = re.compile(r"^\d+(\.\d{1,2})?$")
    r_status = re.compile(r"^(Completed|Pending)$")
    tuple_list = [("Transaction_ID", r_int, "Invalid Transaction Id"), ("Date", r_date, "Invalid Date Format"), 
        ("Quantity", r_float, "Invalid Quantity"), ("Unit_Price", r_float, "Invalid Unit Price"), 
        ("Total_Amount", r_float, "Invalid Transaction Total"), ("Status", r_status, "Status is not Pending/Complete"), 
        ("Customer_Name", None, "Customer name invalid format"), ("Item_Purchased", None, "Item purchased invalid format")]
    #leaving patterns as raw strings makes the cpu pause and transalte every row
    #the pattern is already loaded into memory
    rule_dict = {}
    for key, pattern, comment in tuple_list:
        rule_dict[key] = [pattern, comment]
    for row in df:
        #rule_dict is our complied pattern and run.match on our pandas dataframe.
        if not rule_dict.get("Transaction_ID")[0].match(str(row.get("Transaction_ID"))):
            row["Error"] = rule_dict.get("Transaction_ID")[1]
            error_list.append(row)
            continue
        if not rule_dict.get("Date")[0].match(str(row.get("Date"))):
            row["Error"] = rule_dict.get("Date")[1]
            error_list.append(row)
            continue
        if not rule_dict.get("Quantity")[0].match(str(row.get("Quantity"))):
            row["Error"] = rule_dict.get("Quantity")[1]
            error_list.append(row)
            continue
        if not rule_dict.get("Unit_Price")[0].match(str(row.get("Unit_Price"))):
            row["Error"] = rule_dict.get("Unit_Price")[1]
            error_list.append(row)
            continue
        if not rule_dict.get("Total_Amount")[0].match(str(row.get("Total_Amount"))):
            row["Error"] = rule_dict.get("Total_Amount")[1]
            error_list.append(row)
            continue
        if not rule_dict.get("Status")[0].match(str(row.get("Status"))):
            row["Error"] = rule_dict.get("Status")[1]
            error_list.append(row)
            continue
        try:    row["Total_Amount"] = float(row["Total_Amount"]) 
        except (ValueError, TypeError):
            row["Error"] = "Invalid Total_Amount"
            error_list.append(row) 
            continue
        try: row["Unit_Price"] = float(row["Unit_Price"])
        except (ValueError, TypeError):
            row["Error"] =  "Could not conver unit price into a float"
            error_list.append(row)
            continue
        try:  row["Quantity"] = int(row["Quantity"])
        except (ValueError, TypeError):
            row["Error"] = "Invalid Quantity"
            error_list.append(row)
            continue
        clean_list.append(row)
    if len(error_list) > 0:
        bad_df = pd.DataFrame(error_list)
            #pd automitcally creates our headers using dict keys
        bad_df.to_csv(f"bad_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            #creates a csv file with the bad data
        logger.warning("Data quality issues found in file: %d rows with errors. See bad_data_%s.csv for details.", len(error_list), datetime.now().strftime('%Y%m%d_%H%M%S'))
    return clean_list

def decode_csv(file, filename):
    #use chardet library to detect encoding of file 
    #red the file then detect the encoding
    usecols = ["Transaction_ID", "Date", "Customer_Name", "Item_Purchased", "Quantity", "Unit_Price", "Total_Amount", "Status"]
    #only allow chardet_result to read a chunk of the file encoding into memory 
    chunk_size = 1024
    #detects the f.read(chunksize)
    chardet_result = chardet.detect(file.read(chunk_size))
    encoding = chardet_result["encoding"]
    #reset cursor from fread
    file.seek(0)
    try:
        #use pd to read the csv file and load it into memory
        csv_data = pd.read_csv(file, encoding=encoding, usecols=usecols)
        #replace any null values with None and then convert the dataframe to a list of dicts
        csv_data = csv_data.where(pd.notnull(csv_data), None)
        csv_dict = csv_data.to_dict(orient="records")
        return csv_dict
    except UnicodeDecodeError:
        logger.warning("Failed to decode file with detected encoding: %s file: %s", encoding, filename)
    except Exception as e:
        logger.error("Unexpected Error in decode_csv module %s", e)
