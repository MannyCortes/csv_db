# handles python logic formatting, checking for empty cells
import logging
import pandas as pd
import pandas.errors as pd_err 
import puremagic

chunk_size = 10000

def file_type_check(file_path):
    try:
        file_type = puremagic.from_file(file_path)
        if file_type == ".csv": process_csv(file_path) 
    except FileNotFoundError:
        print(f"File not path not found: {file_path}") 
    except puremagic.PureValueError:
        print(f"File is empty: {file_path}") 
    except puremagic.PureError:
        print(f"Could not determine file type for: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_csv(file_path):
    try:
        #if no header use the names parameter to provide column names, if header is present use header=0 to read the first row as column names
        #use_coles is a param for pandas to read, contains our column names
        use_cols =[]
        #if needed we can also chunk our pd.read_csv to manage memory for large csv files, but for now we will read the whole file at once
        csv_data = pd.read_csv(file_path, usecols=use_cols)
        csv_data = csv_data.fillna(None)
        #read_csv automatically manages iterating row ids, we can ovverried thisusing index_col="id"
        # if no header in csv file use names parameter'
    except UnicodeDecodeError: 
        print(f"File encoding is not supported for: {file_path}")
        decode_csv(file_path)
    except pd_err.ParserError:  print(f"Error parsing CSV file: {file_path}. Please check the file format and content")
    except FileNotFoundError:   print(f"File not path not found: {file_path}")
    except ValueError:  print(f"Paramaters provided are invalid for reading the csv file")

def decode_csv(file_path): 
    pass

def main():
    # example  
    file_path = r"C:\Users\manny\OneDrive\Pictures\133869629777306621.jpg"
    file_type_check(file_path)
if __name__ == "__main__":    main()