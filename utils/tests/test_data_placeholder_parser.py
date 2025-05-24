import pytest
from utils.data_placeholder_parser import DataPlaceholderParser

parser = DataPlaceholderParser(locale="en_US", seed=42)

@pytest.mark.parametrize("template", [
    "{{text[8]}}",
    "{{text[3-12]}}",
    "{{number[4]}}",
    "{{number[2-6]}}",
    "{{phone[9]}}",
    "{{phone[7-10]}}",
    "{{full_name}}",
    "{{first_name}}",
    "{{surname}}",
    "{{email}}",
    "{{company}}",
    "{{domain}}",
    "{{uuid}}",
    "{{boolean}}",
    "{{choice[a,b,c]}}",
    "{{date[2020]}}",
    "{{date[2020-01 - 2025-05-15]}}",
    "{{sentence[5]}}",
    "{{paragraph[2]}}",
    "{{username}}",
    "{{password[8-12]}}",
    "{{address}}",
    "{{city}}",
    "{{country}}",
    "{{postcode}}",
    "{{state}}",
    "{{ipv4}}",
    "{{ipv6}}",
    "{{mac_address}}",
    "{{url}}",
    "{{slug}}",
    "{{currency}}",
    "{{price[10-100]}}",
    "{{credit_card}}",
    "{{iban}}",
    "{{gender}}",
    "{{job}}",
    "{{company_email}}"
])
def test_placeholder_generation(template):
    """
    Test all supported placeholder patterns to ensure they are parsed and replaced correctly.
    """
    result = parser.replace_placeholders(template)
    assert isinstance(result, str)
    assert not result.startswith("{{")  # should be replaced

def test_combined_placeholders():
    """
    Test multiple placeholders in a single input string.
    """
    template = (
        "User {{first_name}} {{surname}} ({{email}}) works at {{company}} "
        "and uses {{phone[9]}}. Location: {{address}}, {{city}}, {{country}}."
    )
    result = parser.replace_placeholders(template)
    assert "{{" not in result
    assert isinstance(result, str)
    assert "@" in result
    assert len(result) > 0

def test_choice_placeholder():
    """
    Ensure 'choice' placeholder selects only from provided options.
    """
    template = "{{choice[yes,no,maybe]}}"
    for _ in range(10):
        result = parser.replace_placeholders(template)
        assert result in ["yes", "no", "maybe"]
