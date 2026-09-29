from questionary import Style as QStyle
from rich.console import Console

console = Console()

# Questionary style
Q_STYLE = QStyle(
    [
        ("qmark", "fg:#00d7ff bold"),  # ⟫ prompt mark
        ("question", "fg:#ffffff bold"),
        ("answer", "fg:#00d7ff bold"),
        ("pointer", "fg:#00d7ff bold"),
        ("highlighted", "fg:#ffffff bg:#005f87 bold"),
        ("selected", "fg:#00d7ff"),
        ("separator", "fg:#444444"),
        ("instruction", "fg:#888888 italic"),
    ]
)


def q(func, *args, **kwargs):
    """Execute a questionary prompt and handle KeyboardInterrupt by returning None"""
    result = func(*args, style=Q_STYLE, **kwargs).ask()
    if result is None:
        raise KeyboardInterrupt
    return result
