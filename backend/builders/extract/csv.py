"""CSV extract configuration builder."""
import os
from typing import Any


def clean_profile_data(profile_data: Any, exclude_keys: list[str] | None = None) -> Any:
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
            'counts',
            'block_alias_counts',
            'category_alias_counts',
            'script_counts',
            'n_scripts',
            'n_characters_distinct'

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