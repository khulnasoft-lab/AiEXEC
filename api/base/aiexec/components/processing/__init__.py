"""Processing components for AiExec."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiexec.components._importing import import_mod

if TYPE_CHECKING:
    from aiexec.components.processing.alter_metadata import AlterMetadataComponent
    from aiexec.components.processing.batch_run import BatchRunComponent
    from aiexec.components.processing.combine_text import CombineTextComponent
    from aiexec.components.processing.converter import TypeConverterComponent
    from aiexec.components.processing.create_data import CreateDataComponent
    from aiexec.components.processing.data_operations import DataOperationsComponent
    from aiexec.components.processing.data_to_dataframe import DataToDataFrameComponent
    from aiexec.components.processing.dataframe_operations import DataFrameOperationsComponent
    from aiexec.components.processing.extract_key import ExtractDataKeyComponent
    from aiexec.components.processing.filter_data import FilterDataComponent
    from aiexec.components.processing.filter_data_values import DataFilterComponent
    from aiexec.components.processing.json_cleaner import JSONCleaner
    from aiexec.components.processing.lambda_filter import LambdaFilterComponent
    from aiexec.components.processing.llm_router import LLMRouterComponent
    from aiexec.components.processing.merge_data import MergeDataComponent
    from aiexec.components.processing.message_to_data import MessageToDataComponent
    from aiexec.components.processing.parse_data import ParseDataComponent
    from aiexec.components.processing.parse_dataframe import ParseDataFrameComponent
    from aiexec.components.processing.parse_json_data import ParseJSONDataComponent
    from aiexec.components.processing.parser import ParserComponent
    from aiexec.components.processing.prompt import PromptComponent
    from aiexec.components.processing.python_repl_core import PythonREPLComponent
    from aiexec.components.processing.regex import RegexExtractorComponent
    from aiexec.components.processing.save_file import SaveToFileComponent
    from aiexec.components.processing.select_data import SelectDataComponent
    from aiexec.components.processing.split_text import SplitTextComponent
    from aiexec.components.processing.structured_output import StructuredOutputComponent
    from aiexec.components.processing.update_data import UpdateDataComponent

_dynamic_imports = {
    "AlterMetadataComponent": "alter_metadata",
    "BatchRunComponent": "batch_run",
    "CombineTextComponent": "combine_text",
    "TypeConverterComponent": "converter",
    "CreateDataComponent": "create_data",
    "DataOperationsComponent": "data_operations",
    "DataToDataFrameComponent": "data_to_dataframe",
    "DataFrameOperationsComponent": "dataframe_operations",
    "ExtractDataKeyComponent": "extract_key",
    "FilterDataComponent": "filter_data",
    "DataFilterComponent": "filter_data_values",
    "JSONCleaner": "json_cleaner",
    "LambdaFilterComponent": "lambda_filter",
    "LLMRouterComponent": "llm_router",
    "MergeDataComponent": "merge_data",
    "MessageToDataComponent": "message_to_data",
    "ParseDataComponent": "parse_data",
    "ParseDataFrameComponent": "parse_dataframe",
    "ParseJSONDataComponent": "parse_json_data",
    "ParserComponent": "parser",
    "PromptComponent": "prompt",
    "PythonREPLComponent": "python_repl_core",
    "RegexExtractorComponent": "regex",
    "SaveToFileComponent": "save_file",
    "SelectDataComponent": "select_data",
    "SplitTextComponent": "split_text",
    "StructuredOutputComponent": "structured_output",
    "UpdateDataComponent": "update_data",
}

__all__ = [
    "AlterMetadataComponent",
    "BatchRunComponent",
    "CombineTextComponent",
    "CreateDataComponent",
    "DataFilterComponent",
    "DataFrameOperationsComponent",
    "DataOperationsComponent",
    "DataToDataFrameComponent",
    "ExtractDataKeyComponent",
    "FilterDataComponent",
    "JSONCleaner",
    "LLMRouterComponent",
    "LambdaFilterComponent",
    "MergeDataComponent",
    "MessageToDataComponent",
    "ParseDataComponent",
    "ParseDataFrameComponent",
    "ParseJSONDataComponent",
    "ParserComponent",
    "PromptComponent",
    "PythonREPLComponent",
    "RegexExtractorComponent",
    "SaveToFileComponent",
    "SelectDataComponent",
    "SplitTextComponent",
    "StructuredOutputComponent",
    "TypeConverterComponent",
    "UpdateDataComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import processing components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
