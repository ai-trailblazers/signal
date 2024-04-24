import logging

from agents.assistant import Assistant
from agents.pm import PM

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application is running. Press Ctrl+C to exit.")
    
    assistant = Assistant()
    pm = PM()

    assistant.subscribe(pm)
    pm.subscribe(assistant)

    pm.online()
    assistant.online()
    
    assistant.dispose()
    pm.dispose()

if __name__ == "__main__":
    main()
