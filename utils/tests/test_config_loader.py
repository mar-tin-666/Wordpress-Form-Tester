import pytest
import tempfile
import os
from utils.config_loader import load_config


def test_load_valid_config_file():
    """
    Test that a valid YAML file is correctly loaded into a dictionary.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml") as tmp:
        tmp.write("key: value\nnumber: 42")
        tmp_path = tmp.name

    try:
        config = load_config(tmp_path)
        assert config["key"] == "value"
        assert config["number"] == 42
    finally:
        os.remove(tmp_path)


def test_load_missing_file_raises_error():
    """
    Test that loading a nonexistent YAML file raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent/config.yaml")


def test_load_invalid_yaml_raises_error():
    """
    Test that loading an invalid YAML file raises ValueError with a proper message.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml") as tmp:
        tmp.write("key: [1, 2\n")  # Invalid YAML (missing closing bracket)
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError) as exc_info:
            load_config(tmp_path)
        assert "Invalid YAML file" in str(exc_info.value)
    finally:
        os.remove(tmp_path)

