import yaml
import os
from utils.data_placeholder_parser import DataPlaceholderParser

def load_config_with_placeholders(path: str = "config/default.yaml") -> dict:
    """
    Loads a YAML configuration file and replaces all placeholder values using DataPlaceholderParser.

    Args:
        path (str): Path to the YAML config file. Defaults to "config/default.yaml".

    Returns:
        dict: Parsed configuration with placeholders resolved.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the YAML file is invalid.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at: {path}")
    
    with open(path, "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

    parser = DataPlaceholderParser(locale=config.get("locale", "en_US"))

    def resolve_placeholders(data):
        if isinstance(data, dict):
            return {k: resolve_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [resolve_placeholders(item) for item in data]
        elif isinstance(data, str):
            return parser.replace_placeholders(data)
        return data

    return resolve_placeholders(config)

