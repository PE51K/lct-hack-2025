from fastapi import FastAPI
import models
from models import extract, sources
from postgres import PostgresExtractConfigBuilder as pg_cfg_builder

app = FastAPI()


@app.get("/get_meta")
async def get_meta(user_input: str):

    src = await recognise_source(user_input)

    if src.source_type == extract.SourceType.folder:
        content_metadata = await get_folder_source_meatdata(src)
    if src.source_type  == extract.SourceType.kafka:
        content_metadata = await get_kafka_source_meatdata(src)
        src.content_type = extract.ContentType.json
    if src.source_type  == extract.SourceType.PostgreSQL:
        src.connection_string = await pg_cfg_builder.get_connection_data(user_input)
        table_name = await pg_cfg_builder.get_table_name(user_input)
        src.content_type = extract.ContentType.table
        cnt = await pg_cfg_builder.get_content_metadata(src, table_name)

    else:
        content_metadata = extract.Content(
            message_name = "n/a"
        )

    return extract.ExtractConfig(
        source_metadata = src,
        content_metadata = cnt
    )
    
    extract_config.content_metadata = content_metadata

    return extract_config

async def recognise_source(source: str) -> extract.Source:
    """ определяем тех тип источника и строку подклчюения по ввводу """

    if "file:" in source:
        src = extract.Source(
            source_type = extract.SourceType.folder
        )
    elif "kafka:" in source:
        src = extract.Source(
            source_type = extract.SourceType.kafka
        )
    elif "postgresql:" in source:
        src = extract.Source(
            source_type = extract.SourceType.PostgreSQL
        )
    else:
        src = extract.Source(
            source_type = extract.SourceType.na,
            connection_string = ""
        )

    return src

async def get_folder_source_meatdata(connection_string: str) -> list[extract.Content]:
    """ определяем метаданные содержимого папки """
    cont = [extract.Content(
        message_name = "csv"
    )]

    return cont

async def get_kafka_source_meatdata(connection_string: str) -> list[extract.Content]:
    """ определяем метаданные содержимого kafka """
    cont = [extract.Content(
        message_name = "csv"
    )]

    return cont

async def get_pg_source_meatdata(connection_string: str) -> list[extract.Content]:
    """ определяем метаданные содержимого kafka """
    cont = [extract.Content(
        message_name = "csv"
    )]

    return cont

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)