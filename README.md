# 🧪 Wordpress Form Tester (in Python with Playwright & Email Validation)

This project provides automated end-to-end tests for Wordpress forms using [Playwright](https://playwright.dev/python/) and `pytest`.  
It supports dynamic configuration via YAML, and validates not only the form behavior but also the content of confirmation emails (including attachments).
Prepared and tested on Wordpress forms based on Contact Form 7.

---

## Features

- Submits web forms based on YAML-defined structure
- Validates form error messages for required fields
- Checks autoresponder and internal (admin/HR) email content
- Verifies attached files in emails
- Works in headless mode (default) - if you want to change edit the conftest.py file

---

## Installation

```bash
pip install -r requirements.txt
playwright install
```

---

## Configuration

Create a YAML config file with your form specification in `config/form` (i.e. `config/form/form_config.yaml`).  
Example file: `config/form/form_config_example.yaml`.  
This file defines:
- Target URL
- Form field structure
- Validation messages
- Email access credentials
- Expected email content


## Running the Tests

```bash
pytest
```

### Headless / Headed

```bash
HEADLESS=true pytest      # default
HEADLESS=false pytest     # run with visible browser
```

---

## Directory Structure

```
│
├── tests/                                  # Wordpress tests (main functionality)
│   └── e2e/                                # E2E Tests
│       └── test_universal_form.py          # Form validation tests 
├── config/                                 # YAML configuration files for form structure, validation, and test scenarios
|   └── form/                               # Configs for forms
│       ├── form_config.yaml                # Main test configuration for the target form and email (you have to create it!)
│       └── form_config_example.yaml        # Example config
├── resources/                              # Files used for upload in form tests (e.g. sample PDFs)
│   ├── file.pdf                            # Example PDF file for upload tests
│   └── file.txt                            # Example TXT file for upload tests
├── pages/                                  # Page Object for form interaction
│   └── form_page.py                        # Page Object for form field interaction with Playwright
├── utils/                                  # Utility modules used by tests
│   ├── tests/                              # Unit tests for utils
│   │   ├── test_config_loader.py           # Unit tests for YAML config loader
│   │   ├── test_data_placeholder_parser.py # Unit tests for data placeholder
│   │   └── test_email_checker.py           # Unit tests for email parsing and content checks
│   ├── config_loader.py                    # YAML config loader
│   ├── data_placeholder_parser.py          # Flexible data placeholder parser for generating dynamic test data
│   └── email_checker.py                    # Handles IMAP login and email validation logic
├── .gitignore                              # .gitignore file  
├── contest.py                              # Shared fixtures and Playwright browser setup
├── LICENSE                                 # Apache 2.0 License
├── pytest.ini                              # Pytest configuration (e.g. verbosity, markers)
├── requirements.txt                        # List of Python dependencies
└── README.md                               # Project overview and usage instructions


### 🧩 Placeholdery danych testowych (`{{...}}`)

Form input values can be dynamically generated za pomocą specjalnych placeholderów w polach `value:` w pliku YAML, np.:

```yaml
full-name:
  value: "{{full_name}}"
email:
  value: "{{email}}"
phone:
  value: "{{phone[9]}}"
comment:
  value: "Some comments: {{sentence[4]}}"
```

Supported placeholders include::
- personal (`full_name`, `first_name`, `surname`, `email`, `phone`)
- network (`ipv4`, `ipv6`, `mac_address`)
- finance (`credit_card`, `price[10-500]`)
- dates (`date[2020-01 - 2023-12-31]`)
- and many more – see the full list in the `DataPlaceholderParser`.


### Form auto-tests

Tests are automatically parameterized for every `.yaml` in folder `config/form/`:
- All files `config/form/*.yaml` are included,
- Files containing `_example.yaml` are **skipped**,
- Each test verifies the correctness of kconfig, placeholders i data form structure.


---

## License

Apache 2.0
