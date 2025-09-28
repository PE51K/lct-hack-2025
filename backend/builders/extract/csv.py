"""CSV extract configuration builder."""
import json
import os
from typing import Optional, Any

import pandas as pd
from ydata_profiling import ProfileReport

from . import BaseExtractConfigBuilder
from models.extract import Content, ContentType, Source


SAMPLE_SIZE = 10000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'part1.csv')


def clean_profile_data(profile_data: Any, exclude_keys: list[str] | None) -> Any:
    """Рекурсивная очистка указанных ключей из данных профиля."""
    if exclude_keys is None:
        exclude_keys = [
            'value_counts_without_nan',
            'value_counts_index_sorted',
            'value_counts',
            'value_counts_with_nan',
            'histogram_data',
            'histogram_frequency',
            'mini_histogram',
            'first_rows',
            'length_histogram',
            'histogram_length',
            'bin_edges',
            'character_counts',
            'category_alias_values',
            'block_alias_values',
            'block_alias_char_counts',
            'script_char_counts',
            'category_alias_char_counts',
            'word_counts',
            'histogram',
            'counts'
        ]

    if isinstance(profile_data, dict):
        return {
            key: clean_profile_data(value, exclude_keys)
            for key, value in profile_data.items()
            if key not in exclude_keys
        }
    elif isinstance(profile_data, list):
        return [clean_profile_data(item, exclude_keys) for item in profile_data]
    else:
        return profile_data


def data_extractor():
    """Функция для извлечения данных из CSV файла и создания профиля."""
    try:
        # Определяем разделитель
        separators = [',', ';', '\t', '|']

        for sep in separators:
            try:
                df = pd.read_csv(FILE_PATH,sep=sep,
                                 on_bad_lines='skip',
                                 engine='python',
                                 nrows=SAMPLE_SIZE)
                if df.shape[1] > 1:
                    print(f"Найден разделитель: '{sep}'")
                    break
            except (pd.errors.ParserError,
                    pd.errors.EmptyDataError,
                    UnicodeDecodeError,
                    Exception) as e:
                print(f"Ошибка при проверке разделителя '{sep}': {e}")
                continue
        else:
            # Если не нашли разделитель, используем стандартный
            sep = ','
            print("Используем стандартный разделитель ','")

            # Read with right separator
            df = pd.read_csv(FILE_PATH, sep=sep, on_bad_lines='skip',
                             engine='python', nrows=SAMPLE_SIZE)

        print(f"Загружено {len(df)} строк, {df.shape[1]} колонок")
        print("Колонки:", list(df.columns))

        # Создание профиля
        profile = ProfileReport(df, title="Profiling Report", explorative=True)

        # Конвертация отчета в JSON
        profile_json = profile.to_json()

        # Вывод структуры JSON
        data = json.loads(profile_json)
        cleaned_data = clean_profile_data(data)

        # Извлекаем только variables и table
        variables_data = cleaned_data.get('variables', {})
        table_data = data.get('table', {})
        print(f'Общая метаинформация о таблице (количество переменных, наблюдений, пропусков):\n'
              f'{json.dumps(table_data, indent=2, ensure_ascii=False)}')
        print(f'Статистика по каждой колонке:\n'
              f'{json.dumps(variables_data, indent=2, ensure_ascii=False)}')

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


class CsvExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for CSVsource configurations.

    Extracts metadata from CSV sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from CSV source."""
        raise NotImplementedError("Metadata extraction not implemented for CSV sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for CSV source.

        Args:
            source: CSV source configuration.

        Returns:
            ContentType for CSV.
        """
        raise NotImplementedError("Content type extraction not implemented for CSV sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> str:
        """Get statistics for CSV source content.

        Args:
            source: CSV source configuration.

        Returns:
            String with content statistics.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for CSV sources."
        )
