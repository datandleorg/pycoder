import json
import os
import time

from app.utils.config import handle_arguments, init_config, load_config


CONFIG_FILE = "config.json"



def init_app():
    # Check if the configuration file exists; if not, initiate setup
    if not os.path.exists(CONFIG_FILE):
        init_config()

    # Load the configuration for later use in the CLI
    config = load_config()
    print(f"Welcome back")
    for key, value in config.items():
            print(f"{key}: {value}")

    # Handle the command-line arguments
    handle_arguments(config)


    # Initialize codebase loader and load all files
    loader = CodebaseLoader(config)
    loader.load_codebase()

    # Set up file system monitoring
    event_handler = CodeChangeHandler(loader)
    observer = Observer()
    observer.schedule(event_handler, path=loader.code_base_path, recursive=True)
    observer.start()
    print(f"Watching for changes in: {loader.code_base_path}")

    init_graph()

    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()