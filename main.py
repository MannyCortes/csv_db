#imports modules and runs them effectively
import transform 
import load
from fastapi import FastAPI, UploadFile, File



    #fastapi dev filename.py to run
app = FastAPI()
#path operation decorator
# files less than 1mb kept on memory else sent to disk and can be adjust below
#MultiPartParser.max_file_sized = 2 * 1024*1024
@app.post("/upload") #POST is when a user is providing the server with a file
#File as a parameter tells python to search for things other than a json
async def main(file: UploadFile = File(...)): #async optional if await method is needed 
    if transform.file_type_check(file.file): 
        try:
            #file is now wrapped in an object pandas doesnt recognize, pull file our using.file attribute
            csv_list = transform.process_csv(file.file)
            if csv_list is not None:
                csv_list = transform.csv_df_check(csv_list)
                if csv_list:
                    session = load.initialize_db()
                    load.process(csv_list, session)
        except Exception as e:
            print(f"Error occurred while processing CSV file: {e}")
    
if __name__ == "__main__":
    main()