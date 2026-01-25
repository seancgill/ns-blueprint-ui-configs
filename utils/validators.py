import re
import os
import mimetypes
import json

def validate_extension(extension, logger=None):
    if not extension.isdigit():
        raise ValueError("Extension must be numeric (e.g., 1001).")
    if logger:
        logger.info(f"Validated extension: {extension}")
    return extension

def validate_email(email, logger=None):
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA.Z0-9-.]+$')
    if not email_pattern.match(email):
        raise ValueError("Invalid email format (e.g., user@domain.com).")
    if logger:
        logger.info(f"Validated email: {email}")
    return email

def validate_name(name, field_name, logger=None):
    if not name:
        raise ValueError(f"{field_name} cannot be empty.")
    if logger:
        logger.info(f"Validated {field_name.lower()}: {name}")
    return name

def validate_url(url, logger=None):
    if not url.strip():
        raise ValueError("URL cannot be empty.")
    if not re.match(r"^https?://[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", url):
        raise ValueError("Invalid API URL. Please enter a valid URL (e.g., https://api.example.ucaas.tech).")
    if logger:
        logger.info(f"Validated API URL: {url}")
    return url

def validate_area_code(area_code, logger=None):
    if not area_code.isdigit() or len(area_code) != 3:
        raise ValueError("Area code must be a 3-digit numeric value (e.g., 310).")
    if logger:
        logger.info(f"Validated area code: {area_code}")
    return area_code
'''
def validate_domain_name(domain, logger=None, strict_validation=True):
    """
    Validates a NetSapiens domain name based on strict validation rules.
    
    Args:
        domain (str): The domain name to validate.
        logger (logging.Logger, optional): Logger for logging validation info.
        strict_validation (bool, optional): Enforces strict rules (letters, numbers, periods only; starts with letter).
    
    Returns:
        str: The validated domain name.
    
    Raises:
        ValueError: If the domain name does not meet the validation criteria.
    """
    if not domain.strip():
        raise ValueError("Domain name cannot be empty.")

    # Check character limit (recommended <= 45 characters)
    if len(domain) > 45:
        raise ValueError("Domain name must be 45 characters or less.")

    # Check for trailing period
    if domain.endswith("."):
        raise ValueError("Domain name cannot end with a period (e.g., 'CR.Test.' is invalid).")

    # Strict validation: starts with letter, allows letters, numbers, periods only
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9.]*$')
    if not pattern.match(domain):
        raise ValueError("Domain name must start with a letter and contain only letters, numbers, and periods (e.g., 'CR.Test').")

    if logger:
        logger.info(f"Validated domain: {domain}")
    return domain
''' 


def validate_domain_name(domain, logger=None, strict_validation=True):
    """
    Validates a NetSapiens domain name based on strict validation rules.
    
    Args:
        domain (str): The domain name to validate.
        logger (logging.Logger, optional): Logger for logging validation info.
        strict_validation (bool, optional): Enforces strict rules (letters, numbers, periods, hyphens only; starts with letter).
    
    Returns:
        str: The validated domain name.
    
    Raises:
        ValueError: If the domain name does not meet the validation criteria.
    """
    if not domain.strip():
        raise ValueError("Domain name cannot be empty.")

    # Check character limit (recommended <= 45 characters)
    if len(domain) > 45:
        raise ValueError("Domain name must be 45 characters or less.")

    # Check for trailing period
    if domain.endswith("."):
        raise ValueError("Domain name cannot end with a period (e.g., 'CR.Test.' is invalid).")

    # Strict validation: starts with letter, allows letters, numbers, periods, hyphens only
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9.-]*$')
    if not pattern.match(domain):
        raise ValueError("Domain name must start with a letter and contain only letters, numbers, periods, and hyphens (e.g., 'cirkel-sandbox' or 'CR.Test').")

    if logger:
        logger.info(f"Validated domain: {domain}")
    return domain

def validate_caller_id_number(caller_id_number, field_name, logger=None):
    if not caller_id_number.isdigit() or len(caller_id_number) not in [10, 11]:
        raise ValueError(f"{field_name} must be a numeric value with 10 or 11 digits (e.g., 1234567890 or 11234567890).")
    if logger:
        logger.info(f"Validated {field_name.lower()}: {caller_id_number}")
    return caller_id_number

def validate_non_empty_string(value, field_name, logger=None):
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    if logger:
        logger.info(f"Validated {field_name.lower()}: {value}")
    return value

def validate_image_source(image_source, logger=None):
    if image_source.lower() == 'n':
        return image_source, False  # Allow 'n' to skip
    if image_source.startswith("file://"):
        file_path = image_source[7:]  # Strip 'file://' prefix
        if not os.path.exists(file_path):
            raise ValueError(f"Local image file {file_path} not found.")
        if logger:
            logger.info(f"Validated local image file: {file_path}")
        return file_path, True  # (path, is_local)
    else:
        url_pattern = re.compile(r'^https?://[^\s<>"]+|www\.[^\s<>"]+')
        if not url_pattern.match(image_source):
            raise ValueError("Invalid image URL. Must be a valid URL (e.g., https://example.com/image.jpg) or a local file path with 'file://' prefix.")
        if logger:
            logger.info(f"Validated image URL: {image_source}")
        return image_source, False  # (url, is_local)

def validate_file_path(file_path, logger=None):
    if not os.path.exists(file_path):
        raise ValueError(f"File {file_path} not found. Please create this file or specify a different one.")
    if logger:
        logger.info(f"Validated file path: {file_path}")
    return file_path

def validate_image_file(file_path, logger=None):
    mime_type = mimetypes.guess_type(file_path)[0]
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"File {file_path} is not a recognized image type.")
    if logger:
        logger.info(f"Validated image file: {file_path} (MIME type: {mime_type})")
    return mime_type

def validate_sip_uri(sip_uri, logger=None):
    sip_pattern = re.compile(r'^sip:[0-9\*\?]+@[\w\-\.\*]+$')
    if not sip_pattern.match(sip_uri):
        raise ValueError("Invalid SIP URI format (e.g., sip:1??????????@*).")
    if logger:
        logger.info(f"Validated SIP URI: {sip_uri}")
    return sip_uri

def validate_hex_color(color, logger=None):
    if not re.fullmatch(r"^#([A-Fa-f0-9]{6})$", color):
        raise ValueError("Invalid hex color code. Must be in the format #123abc.")
    if logger:
        logger.info(f"Validated hex color: {color}")
    return color

def validate_yes_no(value, logger=None):
    value = value.lower()
    if value not in ["y", "yes", "n", "no"]:
        raise ValueError("Value must be 'yes' or 'no'.")
    result = "yes" if value in ["y", "yes"] else "no"
    if logger:
        logger.info(f"Validated yes/no value: {result}")
    return result

def validate_yes_no_prompt(prompt, logger=None):
    prompt = prompt.lower()
    if prompt not in ["y", "n"]:
        raise ValueError("Response must be 'y' or 'n'.")
    if logger:
        logger.info(f"Validated yes/no prompt: {prompt}")
    return prompt == "y"

def validate_numeric_range(value, min_value, max_value, logger=None):
    if not value.isdigit() or not (min_value <= int(value) <= max_value):
        raise ValueError(f"Value must be a number between {min_value} and {max_value}.")
    if logger:
        logger.info(f"Validated numeric value: {value} (range: {min_value}-{max_value})")
    return value

def validate_positive_integer(value, field_name, logger=None):
    if not value.isdigit() or int(value) <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    result = int(value)
    if logger:
        logger.info(f"Validated positive integer for {field_name}: {result}")
    return result

def validate_scope(scope, valid_scopes, logger=None):
    scope = scope.lower()
    if scope not in valid_scopes:
        raise ValueError(f"Invalid scope '{scope}'. Must be one of: {', '.join(valid_scopes.keys())}.")
    if logger:
        logger.info(f"Validated scope: {scope}")
    return scope

def validate_ip_address(ip_address, field_name, logger=None):
    ip_pattern = re.compile(r'^(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}|[\w\-\.]+)$')
    if not ip_pattern.match(ip_address):
        raise ValueError(f"{field_name} must be a valid IP address (e.g., 192.168.1.1) or hostname (e.g., a.icr.commio.com).")
    if logger:
        logger.info(f"Validated {field_name.lower()}: {ip_address}")
    return ip_address

def validate_device_suffix(suffix, logger=None):
    """
    Validates a device suffix for additional devices tied to a user extension.
    
    Args:
        suffix (str): The suffix to validate (e.g., 'aa', 'ab').
        logger (logging.Logger, optional): Logger for logging validation info.
    
    Returns:
        str: The validated suffix.
    
    Raises:
        ValueError: If the suffix does not meet the criteria (exactly two lowercase letters).
    """
    if not suffix.strip():
        raise ValueError("Device suffix cannot be empty.")
    if not re.match(r'^[a-z]{2}$', suffix):
        raise ValueError("Device suffix must be exactly two lowercase letters (e.g., 'aa', 'ab').")
    if logger:
        logger.info(f"Validated device suffix: {suffix}")
    return suffix

def load_json_config(file_path, customer_name=None, logger=None):
    validate_file_path(file_path, logger=logger)
    try:
        with open(file_path, 'r') as file:
            configs = json.load(file)
        if not isinstance(configs, list):
            raise ValueError(f"Configuration file {file_path} must contain a JSON array of configurations.")
        for config in configs:
            if not isinstance(config, dict) or "config_name" not in config or "config_value" not in config:
                raise ValueError(f"Each configuration in {file_path} must be an object with 'config_name' and 'config_value'.")
            if customer_name and isinstance(config.get("config_value"), str):
                config["config_value"] = config["config_value"].replace("custID", customer_name)
        if logger:
            logger.info(f"Loaded configurations from {file_path}" + (f" with customer_name: {customer_name}" if customer_name else ""))
            logger.debug(f"Configurations: {json.dumps(configs, indent=2)}")
        return configs
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file {file_path}: {str(e)}")
    

def verify_domain_exists(api_connection, domain, logger=None):
    """
    Checks the NetSapiens API to see if a domain actually exists.
    
    Args:
        api_connection (APIHelper): The active API connection from app.py.
        domain (str): The domain to check.
    
    Returns:
        bool: True if domain exists, False otherwise.
    """
    try:
        # We use the api_connection passed in from the UI
        response = api_connection.get(f"ns-api/v2/domains/{domain}")
        
        if response.status_code == 200:
            if logger: logger.info(f"Verified domain exists: {domain}")
            return True
        else:
            if logger: logger.warning(f"Domain verification failed: {domain} (Status: {response.status_code})")
            return False
            
    except Exception as e:
        if logger: logger.error(f"Error verifying domain: {e}")
        return False