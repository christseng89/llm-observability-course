def print_section(name: str) -> None:
    blue = "\033[94m"
    reset = "\033[0m"
    print(f"\n{blue}{'#' * 60}\n# {name}\n{'#' * 60}{reset}\n")

def print_topic(name: str) -> None:
    brown = "\033[38;5;130m"
    reset = "\033[0m"
    print(f"\n{brown}{'-' * 60}\n# {name}\n{'-' * 60}{reset}\n")


def save_graph_png(app, png_file: str) -> None:
    png_bytes = app.get_graph().draw_mermaid_png()
    with open(png_file, "wb") as f:
        f.write(png_bytes)
    print(f"\033[93mGraph saved to {png_file}\033[0m")
