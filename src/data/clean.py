"""Text cleaning shared by every data source (docs/SCHEMA.md §9)."""
import html
import re

_URL = re.compile(r"https?://\S+|www\.\S+")
_MENTION = re.compile(r"@\w+")
_RT = re.compile(r"^\s*RT\b[:\s]*", flags=re.IGNORECASE)
_HASH = re.compile(r"#(\w+)")
_SPACES = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Strip URLs, @mentions, leading RT and the # of hashtags; unescape HTML; collapse spaces.

    Case is kept on purpose: DistilBERT-uncased lowercases itself, and T5 needs the original casing.
    """
    text = html.unescape(str(text))
    text = _URL.sub(" ", text)
    text = _MENTION.sub(" ", text)
    text = _RT.sub("", text)
    text = _HASH.sub(r"\1", text)
    return _SPACES.sub(" ", text).strip()
