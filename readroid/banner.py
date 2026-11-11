"""Compact, bold ReaDroid terminal banner."""

ART = [
    "██████╗ ███████╗ █████╗ ██████╗",
    "██╔══██╗██╔════╝██╔══██╗██╔══██╗",
    "██████╔╝█████╗  ███████║██║  ██║",
    "██╔══██╗██╔══╝  ██╔══██║██║  ██║",
    "██║  ██║███████╗██║  ██║██████╔╝",
    "╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝",
]


def big_width() -> int:
    return max(len(line) for line in ART)


def render(columns: int, colors: tuple[str, str, str]) -> list[str]:
    _, cyan, reset = colors
    width = max(1, min(int(columns), 78))
    if width < big_width():
        return ["ReaDroid"[:width]]
    gold = "\033[38;5;220m" if reset else ""
    lines = [""]
    for art_line in ART:
        lines.append(f"{gold}{art_line.center(width)}{reset}")
    lines.extend([
        f"{cyan}{'ANDROID APK ANALYSIS'.center(width)}{reset}",
        f"{gold}{'REVERSE ENGINEERING AGENT'.center(width)}{reset}",
        "",
    ])
    return lines
