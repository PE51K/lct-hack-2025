from typing import Any
import sys
from typing import List

from pydantic import model_validator

sys.path.insert(0, ".")

from models.extract import ExtractConfig, SourceType, ContentType, Source, Content
from .kafka import KafkaExtractConfigBuilder


class ExtractConfigBuilder(ExtractConfig):
    """Builder that builds ExtractConfig from provided connection string."""
    source_to_builder_map = {
        SourceType.kafka: KafkaExtractConfigBuilder,
    }

    @model_validator(mode='before')
    @classmethod
    def init_empty_attributes(cls, data: Any) -> Any:
        if not data:
            return({"source_metadata": None, "content_metadata": [], "content_statistics": ""})
        return data
    
    async def recognise_source(source: str) -> Source:
        """определяем тех тип источника и строку подклчюения по ввводу """

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
        """ 
        определяем метаданные содержимого папки 
        
        для этого сначала читаем из источника набор семплов
        для каждого семпла, в зависимости от типа контента вызываем один из стандартных методов 
        """

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

    async def from_uri(self, uri: str) -> ExtractConfig:
        src = await self.recognise_source(uri)

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


if __name__ == "__main__":
    res = ExtractConfigBuilder()
    print(res)
