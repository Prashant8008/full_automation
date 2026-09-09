"""SSB Connect branding helpers for captions and post text."""
import re
import html

BRAND_FOOTER_LINE = "Follow @ssb.connect for daily SSB prep & defence updates."


def clean_article_text(text: str) -> str:
    """Strips RSS boilerplates like 'This article was originally published on...', 'Read the full article on...' etc."""
    if not text:
        return ""
    out = html.unescape(text)
    # Strip "This article was originally published on <domain>."
    out = re.sub(r"This article was originally published on\s+[\w\.\-]+(?:\.|\s*)?", "", out, flags=re.IGNORECASE)
    out = re.sub(r"This article was originally published on\s*.*?(?:\. |\.\n|\n|$)", "", out, flags=re.IGNORECASE)
    # Strip "Read the full article on <domain>: <title>" or similar trailing links
    out = re.sub(r"Read the full article on\s+[^:]+:\s*.*$", "", out, flags=re.IGNORECASE)
    out = re.sub(r"Read more at:?\s*.*$", "", out, flags=re.IGNORECASE)
    out = re.sub(r"Read more on\s+[^:]+:\s*.*$", "", out, flags=re.IGNORECASE)
    # Clean up excess whitespaces
    out = re.sub(r"\s+", " ", out).strip()
    return out


def sanitize_brand_text(text: str) -> str:
    if not text:
        return text
    replacements = [
        (r"follow\s+@?founderswing\s+for\s+daily\s+frameworks?\.?", BRAND_FOOTER_LINE),
        (r"follow\s+founders\s+wing\s+for\s+daily\s+frameworks?\.?", BRAND_FOOTER_LINE),
        (r"@founderswing", "@ssb.connect"),
        (r"founders\s+wing", "SSB Connect"),
        (r"founderswing", "ssb.connect"),
    ]
    out = text
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    out = clean_article_text(out)
    if BRAND_FOOTER_LINE.lower() not in out.lower():
        out = out.rstrip() + "\n\n" + BRAND_FOOTER_LINE
    return out

