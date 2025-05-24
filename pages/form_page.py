from pathlib import Path
from playwright.sync_api import Page

class FormPage:
    """
    Universal form handler using Playwright and YAML config.
    Supports input, textarea, file upload, checkbox, select, and radio inputs.
    """

    def __init__(self, page: Page, config: dict):
        """
        Initializes the FormPage with a Playwright page and test config.

        Args:
            page (Page): Playwright page instance
            config (dict): Parsed YAML config with form URL and fields
        """
        self.page = page
        self.url = config["url"]
        self.fields = config["form_fields"]
        self.success_selector = config["success_selector"]

    def goto(self):
        """Navigates to the form page."""
        self.page.goto(self.url)

    def get_selector(self, field: dict) -> str:
        """
        Constructs a CSS selector for a field based on its type and name.

        Args:
            field (dict): Field definition from config

        Returns:
            str: CSS selector string
        """
        name = field["name"]
        field_type = field.get("type", "text")

        if field_type == "textarea":
            return f"textarea[name='{name}']"
        elif field_type == "file":
            return f"input[type='file'][name='{name}']"
        elif field_type == "checkbox":
            return f"input[type='checkbox'][name='{name}']"
        elif field_type == "radio":
            value = field.get("value")
            if value:
                return f"input[type='radio'][name='{name}'][value='{value}']"
            else:
                return f"input[type='radio'][name='{name}']"
        elif field_type == "select":
            return f"select[name='{name}']"
        else:
            return f"input[name='{name}']"

    def fill_form(self):
        """
        Fills the form with values defined in the YAML config.
        Handles different types of fields appropriately.
        """
        for field in self.fields:
            selector = self.get_selector(field)
            field_type = field.get("type", "text")

            if field_type == "checkbox":
                if field.get("checked", False):
                    self.page.check(selector)
                else:
                    self.page.uncheck(selector)

            elif field_type == "file":
                file_path = Path(field["file"])
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                self.page.set_input_files(selector, str(file_path))

            elif field_type == "select":
                if "value" in field:
                    self.page.select_option(selector, field["value"])
                elif "label" in field:
                    self.page.select_option(selector, label=field["label"])

            elif field_type == "radio":
                self.page.check(selector)

            elif field_type == "textarea" or field_type == "text":
                self.page.fill(selector, field["value"])

            else:
                raise ValueError(f"Unsupported field type: {field_type}")

    def submit(self):
        """Finds and clicks the submit button on the form."""
        self.page.locator("form button[type='submit']").first.click()

    def is_submission_successful(self) -> bool:
        """
        Waits for a success message to appear after submission.

        Returns:
            bool: True if the confirmation is visible
        """
        locator = self.page.locator(self.success_selector)
        locator.wait_for(state="visible", timeout=10000)
        return locator.is_visible()
