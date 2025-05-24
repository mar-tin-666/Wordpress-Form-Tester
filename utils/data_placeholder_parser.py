import re
import random
import string
from faker import Faker
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

class DataPlaceholderParser:
    """
    A flexible data placeholder parser for generating dynamic test data using the {{placeholder[param]}} syntax.

    Supported placeholders include:
        - Basic text: text, number, phone
        - Names and identities: full_name, first_name, surname, username, password
        - Contact: email, company_email, phone
        - Company and location: company, domain, address, city, country, postcode, state
        - System/network: ipv4, ipv6, mac_address, url, slug, uuid
        - Finance: price, currency, credit_card, iban
        - Date/time: date (YYYY, YYYY-MM, full range), sentence, paragraph
        - Other: boolean, choice[a,b,c], gender, job

    Examples:
        "{{phone[9]}}"            -> 9-digit phone number
        "{{text[5-10]}}"          -> random string of 5–10 characters
        "{{choice[yes,no,n/a]}}" -> random value from provided options
        "{{date[2020-01 - 2022-06-30]}}" -> random date between Jan 2020 and Jun 2022

    Args:
        locale (str): Faker locale, e.g., "en_US" or "pl_PL". Defaults to "en_US".
        seed (int, optional): Random seed for reproducible results.

    Methods:
        replace_placeholders(text: str) -> str
            Replaces all {{placeholder}} patterns in a given string with generated data.
    """

    def __init__(self, locale: str = "en_US", seed: int | None = None):
        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)

    def replace_placeholders(self, text: str) -> str:
        """Replaces all placeholders in the given string with corresponding random data."""
        pattern = r"{{([a-zA-Z0-9_]+)(?:\[(.*?)\])?}}"

        def replacer(match):
            name = match.group(1)
            param = match.group(2)
            return self._generate_value(name, param)

        return re.sub(pattern, replacer, text)

    def _parse_range(self, param: str | None) -> tuple[int, int]:
        if not param:
            raise ValueError("Range parameter is required.")
        if '-' in param:
            min_len, max_len = map(int, param.split('-'))
            return min_len, max_len
        val = int(param)
        return val, val

    def _random_string(self, min_len: int, max_len: int) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(min_len, max_len)))

    def _random_digits(self, min_len: int, max_len: int) -> str:
        return ''.join(random.choices(string.digits, k=random.randint(min_len, max_len)))

    def _random_date(self, start: str, end: str) -> str:
        start_date = parse_date(start)
        end_date = parse_date(end)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return (start_date + relativedelta(days=random_days)).date().isoformat()

    def _generate_value(self, name: str, param: str | None) -> str:
        match name:
            case "text":
                if param is None:
                    raise ValueError("The 'text' placeholder requires a length or range, e.g. {{text[5-10]}}")
                return self._random_string(*self._parse_range(param))
            case "number":
                if param is None:
                    raise ValueError("The 'number' placeholder requires a length or range, e.g. {{number[3-6]}}")
                return self._random_digits(*self._parse_range(param))
            case "phone":
                if param is None:
                    raise ValueError("The 'phone' placeholder requires a length or range, e.g. {{phone[9]}}")
                return self._random_digits(*self._parse_range(param))
            case "full_name": return self.faker.name()
            case "first_name": return self.faker.first_name()
            case "surname": return self.faker.last_name()
            case "email": return self.faker.email()
            case "company": return self.faker.company()
            case "domain": return self.faker.domain_name()
            case "uuid": return self.faker.uuid4()
            case "boolean": return str(self.faker.boolean())
            case "choice":
                if not param:
                    raise ValueError("The 'choice' placeholder requires a list of values, e.g. {{choice[a,b,c]}}")
                return random.choice([x.strip() for x in param.split(',')])
            case "date":
                if param is None:
                    raise ValueError("The 'date' placeholder requires a year or range, e.g. {{date[2020-2023]}}")
                if param is None:
                    raise ValueError("The 'date' placeholder requires a year or date range.")

                # Normalize: remove spaces around hyphens used for ranges
                if ' - ' in param:
                    start, end = param.split(' - ')
                    return self._random_date(start.strip(), end.strip())

                if re.match(r"^\d{4}-\d{2}-\d{2}$", param):
                    return param  # already a specific date

                if re.match(r"^\d{4}-\d{2}$", param):
                    return self._random_date(f"{param}-01", f"{param}-28")

                if re.match(r"^\d{4}$", param):
                    return self._random_date(f"{param}-01-01", f"{param}-12-31")

                raise ValueError(f"Invalid date parameter format: {param}")

            case "sentence":
                if param is None:
                    raise ValueError("The 'sentence' placeholder requires a word count, e.g. {{sentence[5]}}")
                return self.faker.sentence(nb_words=int(param))
            case "paragraph":
                if param is None:
                    raise ValueError("The 'paragraph' placeholder requires a sentence count, e.g. {{paragraph[2]}}")
                return self.faker.paragraph(nb_sentences=int(param))
            case "username": return self.faker.user_name()
            case "password":
                if param is None:
                    raise ValueError("The 'password' placeholder requires a length or range, e.g. {{password[8-12]}}")
                return self._random_string(*self._parse_range(param))
            case "address": return self.faker.address().replace('\n', ', ')
            case "city": return self.faker.city()
            case "country": return self.faker.country()
            case "postcode": return self.faker.postcode()
            case "state": return self.faker.state()
            case "ipv4": return self.faker.ipv4()
            case "ipv6": return self.faker.ipv6()
            case "mac_address": return self.faker.mac_address()
            case "url": return self.faker.url()
            case "slug": return self.faker.slug()
            case "currency": return self.faker.currency_code()
            case "price":
                if param is None:
                    raise ValueError("The 'price' placeholder requires a range, e.g. {{price[10-100]}}")
                min_val, max_val = self._parse_range(param)
                return f"{random.uniform(min_val, max_val):.2f}"
            case "credit_card": return self.faker.credit_card_number()
            case "iban": return self.faker.iban()
            case "gender": return random.choice(["male", "female"])
            case "job": return self.faker.job()
            case "company_email": return self.faker.company_email()
            case _:
                return f"{{{{{name}[{param}]}}}}" if param else f"{{{{{name}}}}}"
