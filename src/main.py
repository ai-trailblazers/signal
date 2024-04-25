import logging
import time
import signal
import threading

from agents import VectorDB
from agents.assistant import Assistant
from agents.pm import PM

def setup_signal_handlers(quit_event):
    def signal_handler(signum, frame):
        logging.info("Signal received, shutting down.")
        quit_event.set()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application is running. Press Ctrl+C to exit.")
    vector_db = VectorDB("Signal")
    assistant = Assistant(vector_db)
    pm = PM(vector_db)
    assistant.subscribe(pm)
    pm.subscribe(assistant)
    # pm.online()
    assistant.online()
    quit_event = threading.Event()
    setup_signal_handlers(quit_event)
    try:
        while not quit_event.is_set():
            time.sleep(1)
    finally:
        logging.info("Cleaning up resources.")
        assistant.dispose()
        pm.dispose()
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    main()
