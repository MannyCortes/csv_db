#imports modules and runs them effectively
import transform 
import load

def main():
    file_path = r"C:\Users\manny\OneDrive\Desktop\pdf_db\pressure_test.csv"
    if transform.file_type_check(file_path): 
        try:
            csv_list = transform.process_csv(file_path)
            csv_list = transform.csv_df_check(csv_list)
            if csv_list:
                session = load.initialize_db()
                load.process(csv_list, session)
        except Exception as e:
            print(f"Error occurred while processing CSV file: {e}")
    
if __name__ == "__main__":
    main()