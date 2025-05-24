import pytest
import tempfile
import os
from utils.config_loader import load_config_with_placeholders

def test_load_valid_config_file():
    """
    Test that a valid YAML file with placeholders is correctly loaded and resolved into a dictionary.
    """
    yaml_content = """
locale: pl_PL
form_fields:
  name:
    value: "{{full_name}}"
  phone:
    value: "{{phone[9]}}"
  literal:
    value: "no-placeholder"
"""

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml") as tmp:
        tmp.write(yaml_content)
        tmp_path = tmp.name

    try:
        config = load_config_with_placeholders(tmp_path)
        form = config["form_fields"]

        assert " " in form["name"]["value"]
        assert form["phone"]["value"].isdigit()
        assert len(form["phone"]["value"]) == 9
        assert form["literal"]["value"] == "no-placeholder"

    finally:
        os.remove(tmp_path)


def test_load_missing_file_raises_error():
    """
    Test that loading a nonexistent YAML file raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        load_config_with_placeholders("nonexistent/config.yaml")


def test_load_invalid_yaml_raises_error():
    """
    Test that loading an invalid YAML file raises ValueError with a proper message.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml") as tmp:
        tmp.write("key: [1, 2\n")  # Invalid YAML (missing closing bracket)
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError) as exc_info:
            load_config_with_placeholders(tmp_path)
        assert "Invalid YAML file" in str(exc_info.value)
    finally:
        os.remove(tmp_path)

