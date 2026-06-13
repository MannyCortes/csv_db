from fastapi import FastAPI , UploadFile
from starlette.formparsers import MultiPartParser

#fastapi dev filename.py to run
app = FastAPI()
#path operation decorator
# files less than 1mb kept on memory else sent to disk and can be adjust below
#MultiPartParser.max_file_sized = 2 * 1024*1024
@app.post("/upload") #POST is when a user is providing the server with a file
async def rendpoint(uploaded_file: UploadFile): #async optional if await method is needed 
    content = await uploaded_file.read()
    print(content)