from langchain_core.vectorstores import VectorStoreRetriever

from aiexec.custom.custom_component.custom_component import CustomComponent
from aiexec.field_typing import VectorStore
from aiexec.inputs.inputs import HandleInput


class VectorStoreRetrieverComponent(CustomComponent):
    display_name = "VectorStore Retriever"
    description = "A vector store retriever"
    name = "VectorStoreRetriever"
    icon = "LangChain"

    inputs = [
        HandleInput(
            name="vectorstore",
            display_name="Vector Store",
            input_types=["VectorStore"],
            required=True,
        ),
    ]

    def build(self, vectorstore: VectorStore) -> VectorStoreRetriever:
        return vectorstore.as_retriever()
