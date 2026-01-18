import html

def escape(text: str) -> str:
    """
    Prevent HTML injection and broken markup
    """
    return html.escape(text)
