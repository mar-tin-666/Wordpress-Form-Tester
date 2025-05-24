import pytest
from utils.config_loader import load_config
from pages.form_page import FormPage
from utils.email_checker import EmailChecker
import os
import time


from utils.config_loader import load_config
from pages.form_page import FormPage

@pytest.fixture(scope="session")
def form_config():
    """
    Loads the form config YAML once per test session.
    """
    return load_config("config/form_config.yaml")

def test_submit_button_requires_consent(page, form_config):
    form = FormPage(page, form_config)
    form.goto()

    # Zlokalizuj przycisk submit
    submit_btn = page.locator("form input[type='submit'], form button[type='submit']")

    # Przycisk powinien być nieaktywny na starcie (bo nie ma zaznaczonej zgody)
    assert not submit_btn.is_enabled(), "Submit button should be disabled before consent is checked"

    # Znajdź pole checbox z configa i zaznacz je
    for field in form_config["form_fields"]:
        if field.get("type") == "checkbox" and field.get("required", False):
            selector = form.get_selector(field)
            page.click(selector)

    # Teraz przycisk powinien być aktywny
    assert submit_btn.is_enabled(), "Submit button should be enabled after consent is checked"


def test_submit_with_only_required_checkboxes(page, form_config):
    form = FormPage(page, form_config)
    form.goto()

    # Zaznacz tylko wymagane checkboxy
    for field in form_config["form_fields"]:
        if field.get("type") == "checkbox" and field.get("required", False):
            selector = form.get_selector(field)
            page.click(selector)

    # Spróbuj wysłać formularz
    submit_btn = page.locator("form input[type='submit'], form button[type='submit']")
    submit_btn.click()
    page.wait_for_timeout(1000)

    # Sprawdź globalny komunikat błędu
    global_error = form_config["validation"]["global_error"]
    assert global_error in page.inner_text("body"), "Global error text not found on page"

    # Sprawdź komunikaty przy wymaganych polach (oprócz checkboxów, które były zaznaczone)
    field_error = form_config["validation"]["field_error"]
    shown_errors = 0

    excluded_fields = ["resume"]
    for field in form_config["form_fields"]:
        if field.get("required", False) and field.get("type") != "checkbox" and field["name"] not in excluded_fields:
            field_name = field["name"]
            selector = form.get_selector(field)

            # Sprawdź czy pole jest puste
            value = page.locator(selector).input_value().strip()

            if not value:
                # Znajdź <span data-name="...">
                wrapper = page.locator(f"span[data-name='{field_name}']")
                # Sprawdź, czy w środku występuje tekst walidacyjny
                inner = wrapper.inner_text().strip()
                assert field_error in inner, f"Expected validation error in <span data-name='{field_name}'>: {inner}"
                shown_errors += 1

    assert shown_errors > 0, "No validation errors shown for required empty fields"


def test_submit_all_required_but_no_file(page, form_config):    
    form = FormPage(page, form_config)
    form.goto()

    # Wypełnij wszystkie wymagane pola z configu
    for field in form_config["form_fields"]:
        if not field.get("required", False) or field.get("exclude", False):
            continue
        selector = form.get_selector(field)
        field_type = field.get("type", "text")
        if field_type == "checkbox":
            # checkboxy klikamy (nie .check) aby aktywować JS
            page.click(selector)
        elif field_type == "file":
            if "file" in field:
                file_path = field["file"]
                assert os.path.exists(file_path), f"File does not exist: {file_path}"
                page.set_input_files(selector, file_path)
        elif field_type == "select":
            if "value" in field:
                page.select_option(selector, field["value"])
            elif "label" in field:
                page.select_option(selector, label=field["label"])
        elif field_type == "radio":
            page.click(selector)
        elif field_type in ("textarea", "text"):
            page.fill(selector, field.get("value", "Test"))

    # Spróbuj wysłać formularz
    submit_btn = page.locator("form input[type='submit'], form button[type='submit']")
    submit_btn.click()
    page.wait_for_timeout(1000)

    # Sprawdź globalny komunikat błędu
    global_error = form_config["validation"]["global_error"]
    assert global_error in page.inner_text("body"), "Global error text not found on page"

    # Sprawdź czy pliku jest bład
    field_error = form_config["validation"]["field_error"]

    shown_errors = 0

    for field in form_config["form_fields"]:
        if not field.get("exclude", False):
            continue
        if field.get("required", False) and field.get("type") != "checkbox":
            field_name = field["name"]
            selector = form.get_selector(field)
            # Sprawdź czy pole jest puste
            value = page.locator(selector).input_value().strip()
            if not value:
                # Znajdź <span data-name="...">
                wrapper = page.locator(f"span[data-name='{field_name}']")
                # Sprawdź, czy w środku występuje tekst walidacyjny
                inner = wrapper.inner_text().strip()
                assert field_error in inner, f"Expected validation error in <span data-name='{field_name}'>: {inner}"
                shown_errors += 1

    assert shown_errors > 0, "No validation errors shown for required empty fields"


def test_submit_all_required_but_wrong_file_type(page, form_config):    
    form = FormPage(page, form_config)
    form.goto()

    # Wypełnij wszystkie wymagane pola z configu
    for field in form_config["form_fields"]:
        if not field.get("required", False):
            continue
        selector = form.get_selector(field)
        field_type = field.get("type", "text")
        if field_type == "checkbox":
            # checkboxy klikamy (nie .check) aby aktywować JS
            page.click(selector)
        elif field_type == "file":
            if "file" in field:
                file_path = field["file-wrong"]
                assert os.path.exists(file_path), f"File does not exist: {file_path}"
                page.set_input_files(selector, file_path)
        elif field_type == "select":
            if "value" in field:
                page.select_option(selector, field["value"])
            elif "label" in field:
                page.select_option(selector, label=field["label"])
        elif field_type == "radio":
            page.click(selector)
        elif field_type in ("textarea", "text"):
            page.fill(selector, field.get("value", "Test"))

    # Spróbuj wysłać formularz
    submit_btn = page.locator("form input[type='submit'], form button[type='submit']")
    submit_btn.click()
    page.wait_for_timeout(1000)

    # Sprawdź globalny komunikat błędu
    global_error = form_config["validation"]["global_error"]
    assert global_error in page.inner_text("body"), "Global error text not found on page"

    # Sprawdź czy pliku jest bład
    field_error = form_config["validation"]["field_error_file_type"]

    shown_errors = 0

    for field in form_config["form_fields"]:
        if field.get("required", False) and field.get("type") == "file":
            field_name = field["name"]
            selector = form.get_selector(field)            
            # Sprawdź czy pole jest puste
            value = page.locator(selector).input_value().strip()
            if value:                
                # Znajdź <span data-name="...">
                wrapper = page.locator(f"span[data-name='{field_name}']")
                # Sprawdź, czy w środku występuje tekst walidacyjny
                inner = wrapper.inner_text().strip()
                assert field_error in inner, f"Expected validation error in <span data-name='{field_name}'>: {inner}"
                shown_errors += 1

    assert shown_errors > 0, "No validation errors shown for required files fields"


def test_submit_all_required_only_and_check_mail(page, form_config):
    form = FormPage(page, form_config)
    form.goto()

    # Wypełnij wszystkie wymagane pola z configu
    for field in form_config["form_fields"]:
        if not field.get("required", False):
            continue

        selector = form.get_selector(field)
        field_type = field.get("type", "text")

        if field_type == "checkbox":
            page.click(selector)
        elif field_type == "file":
            file_path = field["file"]
            assert os.path.exists(file_path), f"File not found: {file_path}"
            page.set_input_files(selector, file_path)
        elif field_type == "select":
            if "value" in field:
                page.select_option(selector, field["value"])
            elif "label" in field:
                page.select_option(selector, label=field["label"])
        elif field_type == "radio":
            page.click(selector)
        else:
            page.fill(selector, field.get("value", "Test"))

    # Kliknij submit
    submit_btn = page.locator("form input[type='submit'], form button[type='submit']")
    submit_btn.click()

    # Sprawdź komunikat sukcesu
    success_text = form_config["validation"]["global_success"]
    page.wait_for_selector(f"text={success_text}", timeout=10000)
    assert success_text in page.inner_text("body"), "Success message not found"

    # Czekamy chwlę zanim sprawdzimy maile
    # Można to zrobić lepiej, ale na razie tak zostawiam
    time.sleep(5)

    # === Autoresponder email ===
    auto_cfg = form_config["email_check"]["autoresponder"]
    auto_checker = EmailChecker(**auto_cfg["imap"])
    assert auto_checker.wait_for_email(
        subject_contains=auto_cfg["subject_contains"],
        timeout_seconds=auto_cfg.get("timeout_seconds", 60)
    ), "Autoresponder email not received"
    auto_checker.check_email_content(auto_cfg, form_config["form_fields"])

    # === copy form email ===
    hr_cfg = form_config["email_check"]["form_copy"]
    hr_checker = EmailChecker(**hr_cfg["imap"])
    assert hr_checker.wait_for_email(
        subject_contains=hr_cfg["subject_contains"],
        timeout_seconds=hr_cfg.get("timeout_seconds", 60)
    ), "HR email not received"
    hr_checker.check_email_content(hr_cfg, form_config["form_fields"])