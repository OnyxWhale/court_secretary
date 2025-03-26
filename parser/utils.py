from .parser import start_parse

def run_parser_in_background(max_pages: int) -> None:
    start_parse(max_pages=max_pages)