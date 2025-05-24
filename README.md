# 🧪 Wordpress Form Tester (in Pytjon with Playwright & Email Validation)

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

Create a YAML file in `config/form_config.yaml`.  
Example file: `config/form_config_example.yaml`.  
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
├── tests/                          # Wordpress tests (main functionality)
│   └── e2e/                        # E2E Tests
│       └── test_universal_form.py  # Form validation tests 
├── config/                         # YAML files defining form structure and validation logic
│   ├── form_config.yaml            # Main test configuration for the target form and email (you have to create it!)
│   └── form_config_example.yaml    # Example config
├── resources/                      # Files used for upload in form tests (e.g. sample PDFs)
│   ├── file.pdf                    # Exmaple PDF file for upload tests
│   └── file.txt                    # Exmaple TXT file for upload tests
├── pages/                          # Page Object for form interaction
│   └── form_page.py                # Page Object for form field interaction with Playwright
├── utils/                          # Utility modules used by tests
│   ├── tests/                      # Unit tests for utils
│   │   ├── test_config_loader.py   # Unit tests for YAML config loader
│   │   └── test_email_checker.py   # Unit tests for email parsing and content checks
│   ├── config_loader.py            # YAML config loader
│   └── email_checker.py            # Handles IMAP login and email validation logic
├── .gitignore                      # .gitignore file  
├── contest.py                      # Shared fixtures and Playwright browser setup
├── LICENSE                         # Apache 2.0 License
├── pytest.ini                      # Pytest configuration (e.g. verbosity, markers)
├── requirements.txt                # List of Python dependencies
└── README.md                       # Project overview and usage instructions

```

---

## License

Apache 2.0
