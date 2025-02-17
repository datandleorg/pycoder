
import argparse
import json


CONFIG_FILE = "config.json"

def init_config():
    """Initialize the configuration by asking the user a series of questions."""
    config = {}

    print("Welcome to the CLI Tool Setup!")
    config["project_name"] = input("Enter the project name: ")
    config["project_description"] = input("Enter the project description: ")
    config["code_base_path"] = input("Enter the codebase path: ")
    config["language"] = input("Enter the language: ")

    
    # Save the configuration to a JSON file
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print("Configuration saved successfully!")


def load_config():
    """Load configuration from the JSON file."""
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
    return config

def handle_arguments(config):
    """Handle the command-line arguments."""
        # Define CLI arguments
    parser = argparse.ArgumentParser(description="CLI Tool with configuration setup")
    parser.add_argument('--show-config', action='store_true', help="Display the current configuration")
    parser.add_argument('--set-config', type=str, help="Set a specific configuration parameter (format: key=value)")

    # Parse arguments
    args = parser.parse_args()

    # Handle the '--show-config' option to display current configuration
    if args.show_config:
        print("Current Configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

    # Handle the '--set-config' option to update a configuration parameter
    elif args.set_config:
        key, value = args.set_config.split("=")
        config[key] = value
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print(f"Updated {key} to {value} in configuration.")