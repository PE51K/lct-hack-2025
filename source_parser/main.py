from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from enum import Enum
import json

app = FastAPI()

SourceType = Enum('Source_type', [('na', 1),('folder', 2),('kafka', 3),])

class Source():

    def __init__(self, type: SourceType = SourceType.na, connection_string: str = ""):
        self.type = type
        self.connection_string = connection_string

    type: SourceType 
    connection_string: str

class Attribute():

    def __init__(self, orderNo: int, name: str, data_type: str):
        self.orderNo = orderNo
        self.name = name
        self.data_type = data_type

    orderNo: int
    name: str
    data_type: str

class Content():

    def __init__(self):
        self.attributes = []

    Attributes: list[Attribute]

    def to_dict(self):
        return self.__dict__

class ExtractMetadata():

    def __init__(self, source_metadata: str, content_metadata: str):
        self.source_metadata = source_metadata
        self.content_metadata = content_metadata

    source_metadata: str
    content_metadata: str

    def to_dict(self):
        return self.__dict__

@app.get("/get_meta")
async def get_meta(user_input: str):

    
    src = await recognise_source(user_input)

    if src.type == "folder":
        content_metadata = await get_folder_source_meatdata(src)
    if src.type == "kafka":
        content_metadata = await get_kafka_source_meatdata(src)
    else:
        content_metadata = Content()

    extractMetadata = ExtractMetadata(source_metadata="", content_metadata="")

    respBody = json.dumps(extractMetadata.to_dict(), ensure_ascii=False)
    
    return JSONResponse(content=respBody)


async def recognise_source(source: str) -> Source:
    """ определяем тех тип источника и строку подклчюения по ввводу """
    src = Source()

    return src

async def get_folder_source_meatdata(connection_string: str) -> Content:
    """ определяем метаданные содержимого папки """
    src = Content()

    return src

async def get_kafka_source_meatdata(connection_string: str) -> Content:
    """ определяем метаданные содержимого kafka """
    src = Content()

    return src

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)