from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field
from enum import Enum
import json

#import kafka_manager

app = FastAPI()

SourceType = Enum('Source_type', [('na', 1),('folder', 2),('PostgreSQL', 3),('ClickHouse', 4),('kafka', 5),('hadoop', 6),('sparkstreaming', 7)])
ContentType = Enum('Content_type', [('na', 1),('csv', 2),('xml', 3),('json', 4),('table', 5),('Parquet', 6)])

class Source(BaseModel):
    source_type: SourceType = SourceType.na
    connection_string: str
    content_type: Optional[ContentType] = None

class Attribute(BaseModel):
    orderNo: int
    name: str
    data_type: Optional[str] = None
    nullable: Optional[bool] = None

class Content(BaseModel):
    message_name: str
    attributes: List[Attribute] = Field(default_factory=list)

class ExtractConfig(BaseModel):
    source_metadata: Optional[Source] = None
    content_metadata: List[Content] = Field(default_factory=list)

@app.get("/get_meta")
async def get_meta(user_input: str):

    src = await recognise_source(user_input)

    if src.source_type == SourceType.folder:
        content_metadata = await get_folder_source_meatdata(src)
        src.content_type = ContentType.csv
    if src.source_type  == SourceType.kafka:
        content_metadata = await get_kafka_source_meatdata(src)
        src.content_type = ContentType.json
    else:
        content_metadata = Content(
            message_name = "n/a"
        )

    content_metadata.attributes.append(Attribute(orderNo=1,name="lol",data_type="string"))

    extract_config = ExtractConfig(
        source_metadata = src
        )
    
    extract_config.content_metadata = content_metadata

    return extract_config

async def recognise_source(source: str) -> Source:
    """ определяем тех тип источника и строку подклчюения по ввводу """

    if "file:" in source:
        src = Source(
            source_type = SourceType.folder,
            connection_string = source.replace("file:", "")
        )
    elif "kafka:" in source:
        src = Source(
            source_type = SourceType.kafka,
            connection_string = source.replace("kafka:", "")
        )
    else:
        src = Source(
            source_type = SourceType.na,
            connection_string = ""
        )

    return src

async def get_folder_source_meatdata(connection_string: str) -> List[Content]:
    """ определяем метаданные содержимого папки """
    cont = [Content(
        message_name = "csv"
    )]

    return cont

async def get_kafka_source_meatdata(connection_string: str) -> List[Content]:
    """ определяем метаданные содержимого kafka """
    cont = [Content(
        message_name = "csv"
    )]

    return cont

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)