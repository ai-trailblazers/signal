import logging

from agents.assistant import Assistant
from agents.pm import PM

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application is running. Press Ctrl+C to exit.")
    
    assistant = Assistant()
    github = PM()

    assistant.subscribe(github)
    github.subscribe(assistant)
    assistant.start()
    
    assistant.dispose()
    github.dispose()

if __name__ == "__main__":
    main()
