import threading
from parser.parser import start_parse

def run_parser_in_background(max_pages=1):
    print(f"Starting parser in background thread with max_pages={max_pages}")
    thread = threading.Thread(target=start_parse, args=(max_pages,), daemon=True)
    thread.start()
    print("Parser thread started")
    return thread