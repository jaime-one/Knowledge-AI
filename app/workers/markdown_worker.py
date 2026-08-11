import re
import unicodedata
from datetime import date

import yaml

from app.models.knowledge_worker import KnowledgeOutput
from app.models.markdown_worker import MarkdownOutput


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


def run_markdown_worker(knowledge: KnowledgeOutput) -> MarkdownOutput:
    filename = f"{slugify(knowledge.title)}.md"

    frontmatter_data = {
        "title": knowledge.title,
        "created": date.today().strftime("%Y-%m-%d"),
        "concepts": ", ".join(knowledge.key_concepts),
    }
    frontmatter = "---\n" + yaml.safe_dump(frontmatter_data, allow_unicode=True, sort_keys=False) + "---\n\n"

    content = frontmatter + f"# {knowledge.title}\n\n" + knowledge.content
    return MarkdownOutput(filename=filename, content=content)
