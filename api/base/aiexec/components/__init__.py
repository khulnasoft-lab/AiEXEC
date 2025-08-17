"""AiExec Components module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiexec.components._importing import import_mod

if TYPE_CHECKING:
    from aiexec.components import (
        Notion,
        agentql,
        agents,
        aiml,
        amazon,
        anthropic,
        apify,
        arxiv,
        assemblyai,
        azure,
        baidu,
        bing,
        cleanlab,
        cloudflare,
        cohere,
        composio,
        confluence,
        crewai,
        custom_component,
        data,
        datastax,
        deepseek,
        docling,
        duckduckgo,
        embeddings,
        exa,
        firecrawl,
        git,
        glean,
        google,
        groq,
        helpers,
        homeassistant,
        huggingface,
        ibm,
        icosacomputing,
        input_output,
        langchain_utilities,
        langwatch,
        lmstudio,
        logic,
        maritalk,
        mem0,
        mistral,
        models,
        needle,
        notdiamond,
        novita,
        nvidia,
        olivya,
        ollama,
        openai,
        openrouter,
        perplexity,
        processing,
        prototypes,
        redis,
        sambanova,
        scrapegraph,
        searchapi,
        serpapi,
        tavily,
        tools,
        twelvelabs,
        unstructured,
        vectorstores,
        vertexai,
        wikipedia,
        wolframalpha,
        xai,
        yahoosearch,
        youtube,
        zep,
    )

_dynamic_imports = {
    "agents": "aiexec.components.agents",
    "data": "aiexec.components.data",
    "processing": "aiexec.components.processing",
    "vectorstores": "aiexec.components.vectorstores",
    "tools": "aiexec.components.tools",
    "models": "aiexec.components.models",
    "embeddings": "aiexec.components.embeddings",
    "helpers": "aiexec.components.helpers",
    "input_output": "aiexec.components.input_output",
    "logic": "aiexec.components.logic",
    "custom_component": "aiexec.components.custom_component",
    "prototypes": "aiexec.components.prototypes",
    "openai": "aiexec.components.openai",
    "anthropic": "aiexec.components.anthropic",
    "google": "aiexec.components.google",
    "azure": "aiexec.components.azure",
    "huggingface": "aiexec.components.huggingface",
    "ollama": "aiexec.components.ollama",
    "groq": "aiexec.components.groq",
    "cohere": "aiexec.components.cohere",
    "mistral": "aiexec.components.mistral",
    "deepseek": "aiexec.components.deepseek",
    "nvidia": "aiexec.components.nvidia",
    "amazon": "aiexec.components.amazon",
    "vertexai": "aiexec.components.vertexai",
    "xai": "aiexec.components.xai",
    "perplexity": "aiexec.components.perplexity",
    "openrouter": "aiexec.components.openrouter",
    "lmstudio": "aiexec.components.lmstudio",
    "sambanova": "aiexec.components.sambanova",
    "maritalk": "aiexec.components.maritalk",
    "novita": "aiexec.components.novita",
    "olivya": "aiexec.components.olivya",
    "notdiamond": "aiexec.components.notdiamond",
    "needle": "aiexec.components.needle",
    "cloudflare": "aiexec.components.cloudflare",
    "baidu": "aiexec.components.baidu",
    "aiml": "aiexec.components.aiml",
    "ibm": "aiexec.components.ibm",
    "langchain_utilities": "aiexec.components.langchain_utilities",
    "crewai": "aiexec.components.crewai",
    "composio": "aiexec.components.composio",
    "mem0": "aiexec.components.mem0",
    "datastax": "aiexec.components.datastax",
    "cleanlab": "aiexec.components.cleanlab",
    "langwatch": "aiexec.components.langwatch",
    "icosacomputing": "aiexec.components.icosacomputing",
    "homeassistant": "aiexec.components.homeassistant",
    "agentql": "aiexec.components.agentql",
    "assemblyai": "aiexec.components.assemblyai",
    "twelvelabs": "aiexec.components.twelvelabs",
    "docling": "aiexec.components.docling",
    "unstructured": "aiexec.components.unstructured",
    "redis": "aiexec.components.redis",
    "zep": "aiexec.components.zep",
    "bing": "aiexec.components.bing",
    "duckduckgo": "aiexec.components.duckduckgo",
    "serpapi": "aiexec.components.serpapi",
    "searchapi": "aiexec.components.searchapi",
    "tavily": "aiexec.components.tavily",
    "exa": "aiexec.components.exa",
    "glean": "aiexec.components.glean",
    "yahoosearch": "aiexec.components.yahoosearch",
    "apify": "aiexec.components.apify",
    "arxiv": "aiexec.components.arxiv",
    "confluence": "aiexec.components.confluence",
    "firecrawl": "aiexec.components.firecrawl",
    "git": "aiexec.components.git",
    "wikipedia": "aiexec.components.wikipedia",
    "youtube": "aiexec.components.youtube",
    "scrapegraph": "aiexec.components.scrapegraph",
    "Notion": "aiexec.components.Notion",
    "wolframalpha": "aiexec.components.wolframalpha",
}

__all__: list[str] = [
    "Notion",
    "agentql",
    "agents",
    "aiml",
    "amazon",
    "anthropic",
    "apify",
    "arxiv",
    "assemblyai",
    "azure",
    "baidu",
    "bing",
    "cleanlab",
    "cloudflare",
    "cohere",
    "composio",
    "confluence",
    "crewai",
    "custom_component",
    "data",
    "datastax",
    "deepseek",
    "docling",
    "duckduckgo",
    "embeddings",
    "exa",
    "firecrawl",
    "git",
    "glean",
    "google",
    "groq",
    "helpers",
    "homeassistant",
    "huggingface",
    "ibm",
    "icosacomputing",
    "input_output",
    "langchain_utilities",
    "langwatch",
    "lmstudio",
    "logic",
    "maritalk",
    "mem0",
    "mistral",
    "models",
    "needle",
    "notdiamond",
    "novita",
    "nvidia",
    "olivya",
    "ollama",
    "openai",
    "openrouter",
    "perplexity",
    "processing",
    "prototypes",
    "redis",
    "sambanova",
    "scrapegraph",
    "searchapi",
    "serpapi",
    "tavily",
    "tools",
    "twelvelabs",
    "unstructured",
    "vectorstores",
    "vertexai",
    "wikipedia",
    "wolframalpha",
    "xai",
    "yahoosearch",
    "youtube",
    "zep",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import component modules on attribute access.

    Args:
        attr_name (str): The attribute/module name to import.

    Returns:
        Any: The imported module or attribute.

    Raises:
        AttributeError: If the attribute is not a known component or cannot be imported.
    """
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        # Use import_mod as in LangChain, passing the module name and package
        result = import_mod(attr_name, "__module__", __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result  # Cache for future access
    return result


def __dir__() -> list[str]:
    """Return list of available attributes for tab-completion and dir()."""
    return list(__all__)


# Optional: Consistency check (can be removed in production)
_missing = set(__all__) - set(_dynamic_imports)
if _missing:
    msg = f"Missing dynamic import mapping for: {', '.join(_missing)}"
    raise ImportError(msg)
