import yaml
import os

def load_config(path: str = "config/default.yaml") -> dict:
    """
    Loads a YAML configuration file and returns it as a Python dictionary.

    Args:
        path (str): The path to the YAML config file. Defaults to "config/default.yaml".

    Returns:
        dict: Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist at the given path.
        ValueError: If the file cannot be parsed as valid YAML.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at: {path}")
    
    with open(path, "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

    return config
