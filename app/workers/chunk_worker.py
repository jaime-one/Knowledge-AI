import yaml
from langchain_text_splitters import MarkdownHeaderTextSplitter

from app.models.markdown_worker import MarkdownOutput
from app.models.chunk_worker import Chunk

HEADERS_TO_SPLIT_ON = [
    ("#", "header_1"),
    ("##", "header_2"),
    ("###", "header_3"),
]


def _split_frontmatter(content: str) -> tuple[dict, str]:
    _, frontmatter_raw, body = content.split("---", 2)
    #Convierte el string en un objeto o dicc de python
    frontmatter = yaml.safe_load(frontmatter_raw)
    return frontmatter, body.strip()


def run_chunk_worker(markdown: MarkdownOutput) -> list[Chunk]:
    frontmatter, body = _split_frontmatter(markdown.content)

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
    docs = splitter.split_text(body)
    chunks = []

    for doc in docs:
        metadata = {**doc.metadata, "source": markdown.filename, "title": frontmatter.get("title")}
        chunk = Chunk(content=doc.page_content, metadata=metadata)
        chunks.append(chunk)

    return chunks
