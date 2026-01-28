import time
import os
from utils.logging_setup import setup_logging
from utils.api_helper import APIHelper
from utils.env_loader import load_env
from utils.validators import validate_url, validate_hex_color, validate_yes_no, validate_numeric_range, validate_non_empty_string, load_json_config, validate_scope

logger = setup_logging()
env_vars = load_env()
API_TOKEN = env_vars["API_TOKEN"]
logger.info(f"Loaded API_TOKEN: {API_TOKEN}")

SCOPE_MAPPING = {
    "su": "Super User",
    "res": "Reseller",
    "om": "Office Manager",
    "adv": "Advanced User",
    "cca": "Call Center Agent",
    "ccs": "Call Center Supervisor"
}

UI_CONFIG_PROMPT_COLOR_HEX = {
    "PORTAL_CSS_PRIMARY_1": "Dark Blue",
    "PORTAL_CSS_PRIMARY_2": "Green",
    "PORTAL_CSS_COLOR_MENU_BAR_PRIMARY_1": "Gray",
    "PORTAL_CSS_COLOR_MENU_BAR_PRIMARY_2": "Dark Blue",
    "PORTAL_WEBPHONE_PWA_BACKGROUND_COLOR": "Gray",
    "PORTAL_WEBPHONE_PWA_THEME_COLOR": "Green",
    "PORTAL_THEME_ACCENT": "Green",
    "PORTAL_THEME_PRIMARY": "Gray",
    "PORTAL_CSS_BACKGROUND": "Dark Blue"

}

YES_NO_CONFIGS = [
    "PORTAL_USERS_DIR_MATCH_FIRSTNAME",
    "PORTAL_THREE_WAY_CALL_DISCONNECT_OTHERS_ON_END",
    "PORTAL_USERS_CALLERID_USE_DROPDOWN_DID_LIST"
]

NUMERIC_CONFIGS = {
    "PORTAL_USERS_SECURE_PASSWORD_MIN_LENGTH": 8,
    "PORTAL_USERS_SECURE_PASSWORD_MIN_CAPITAL_LETTER_COUNT": 1,
    "PORTAL_USERS_SECURE_PASSWORD_MIN_NUMBER_COUNT": 1,
    "PORTAL_USERS_MIN_PASSWORD_LENGTH": 4,
    "PORTAL_USERS_SECURE_PASSWORD_MIN_SPECIAL_CHAR_COUNT": 0
}

STRING_CONFIGS = [
    "PORTAL_LOGGED_IN_POWERED_BY",
    "PORTAL_PHONES_SNAPMOBILE_HOSTID",
    "PORTAL_PHONES_SNAPMOBILE_TITLE",
    "MOBILE_IOS_FEEDBACK_EMAIL",
    "MOBILE_ANDROID_FEEDBACK_EMAIL",
    "PORTAL_EXTRA_JS",
    "MOBILE_REGISTRATION_SERVER",
    "EMAIL_HTML_GET_SUPPORT_LINK"
]

common_payload = {
    "admin-ui-account-type": "*",
    "reseller": "*",
    "user": "*",
    "user-scope": "*",
    "core-server": "*",
    "domain": "*",
    "description": "Created via API"
}

def prompt_for_color(config_name, current_value, default_value):
    while True:
        new_value = input(f"Enter a hex color code for {config_name} (e.g., #123abc) [Current: {current_value} | Default: {default_value}]: ").strip()
        if new_value == "":
            logger.info(f"Using default value '{default_value}' for {config_name}")
            return default_value
        try:
            return validate_hex_color(new_value, logger=logger)
        except ValueError as e:
            print(f"Error: {e}")
            logger.warning(f"Invalid hex color input for {config_name}: {new_value}")

def prompt_for_yes_no(config_name, current_value):
    while True:
        new_value = input(f"Enter 'yes' or 'no' for {config_name} [Current: {current_value}]: ").strip()
        try:
            return validate_yes_no(new_value, logger=logger)
        except ValueError as e:
            print(f"Error: {e}")
            logger.warning(f"Invalid yes/no input for {config_name}: {new_value}")

def prompt_for_numeric(config_name, current_value, min_value=0, max_value=9):
    while True:
        new_value = input(f"Enter a number between {min_value} and {max_value} for {config_name} [Current: {current_value}]: ").strip()
        try:
            return validate_numeric_range(new_value, min_value, max_value, logger=logger)
        except ValueError as e:
            print(f"Error: {e}")
            logger.warning(f"Invalid numeric input for {config_name}: {new_value}")

def prompt_for_string(config_name, current_value):
    while True:
        new_value = input(f"Enter a value for {config_name} [Current: {current_value}]: ").strip()
        try:
            return validate_non_empty_string(new_value, config_name, logger=logger)
        except ValueError as e:
            print(f"Error: {e}")
            logger.warning(f"Invalid string input for {config_name}: {new_value}")

def send_configuration(config, api_url, scope=None):
    payload = common_payload.copy()
    payload["config-name"] = config["config_name"]
    payload["config-value"] = config["config_value"]
    
    if scope:
        payload["user-scope"] = scope
    
    if "reseller" in config:
        payload["reseller"] = config["reseller"]
    
    api_helper = APIHelper(api_url, logger=logger)
    endpoint = "ns-api/v2/configurations"
    
    try:
        start_time = time.time()
        response = api_helper.post(endpoint, payload)
        elapsed_time = time.time() - start_time
        logger.info(f"Sending configuration {config['config_name']} took {elapsed_time:.2f} seconds")
        
        print(f"POST status code for {config['config_name']} (Scope: {scope if scope else 'Default'}, Reseller: {payload['reseller']}): {response.status_code}")
        logger.info(f"POST status code for {config['config_name']} (Scope: {scope if scope else 'Default'}, Reseller: {payload['reseller']}): {response.status_code}")
        
        if response.status_code == 409:
            logger.info(f"Conflict detected for {config['config_name']}, attempting PUT request")
            start_time = time.time()
            response = api_helper.put(endpoint, payload)
            elapsed_time = time.time() - start_time
            logger.info(f"PUT request for {config['config_name']} took {elapsed_time:.2f} seconds")
            print(f"PUT status code for {config['config_name']} (Scope: {scope if scope else 'Default'}, Reseller: {payload['reseller']}): {response.status_code}")
            logger.info(f"PUT status code for {config['config_name']} (Scope: {scope if scope else 'Default'}, Reseller: {payload['reseller']}): {response.status_code}")
        
        return response.status_code
    except Exception as e:
        logger.error(f"Error sending configuration {config['config_name']}: {str(e)}")
        raise


def update_configurations(customer_name=None, config_file=os.path.join("config", "ui_configs.json"), api_url=None):
    print(f"Using API URL: {api_url}")
    logger.info(f"Using API URL: {api_url}")

    # --- 1. ASK ABOUT RESELLER CONFIGS ---
    include_resellers = False
    
    while True:
        user_input = input("Do you want to apply Reseller-specific configs? (yes/no): ").strip()
        try:
            validated_response = validate_yes_no(user_input, logger=logger)
            include_resellers = (validated_response == "yes")
            break
        except ValueError:
            print("Invalid input. Please enter 'yes' or 'no'.")
            
    if not include_resellers:
        print(">> Filtering engaged: Reseller configs will be skipped.")
        logger.info("Skipping reseller configurations per user request.")
    else:
        print(">> Standard mode: All configs will be processed.")

    # --- 2. ASK ABOUT CSS COLOR CONFIGS ---
    include_css_colors = False
    
    while True:
        user_input = input("Do you want to set/change CSS color configurations? (yes/no): ").strip()
        try:
            validated_response = validate_yes_no(user_input, logger=logger)
            include_css_colors = (validated_response == "yes")
            break
        except ValueError:
            print("Invalid input. Please enter 'yes' or 'no'.")
            
    if not include_css_colors:
        print(">> CSS color configs will be skipped.")
        logger.info("Skipping CSS color configurations per user request.")
    else:
        print(">> CSS color configs will be processed - you will be prompted for input.")
        logger.info("CSS color configurations will be prompted.")

    # --- 3. LOAD CONFIGS (DO THIS ONLY ONCE) ---
    configs = load_json_config(config_file, customer_name, logger=logger)
    
    # --- 4. START SINGLE LOOP ---
    for config in configs:
        
        # [A] RESELLER GATEKEEPER CHECK
        if "reseller" in config and not include_resellers:
            continue

        # [B] CSS COLOR GATEKEEPER CHECK
        config_name = config["config_name"]
        if config_name in UI_CONFIG_PROMPT_COLOR_HEX and not include_css_colors:
            # Skip CSS color configs if user said no
            logger.info(f"Skipping CSS color config: {config_name}")
            continue

        # [C] PROCESS THE CONFIG
        current_value = config["config_value"]
        
        # Only prompt for inputs if it is NOT a reseller config
        if "reseller" not in config:
            if config_name in UI_CONFIG_PROMPT_COLOR_HEX:
                config["config_value"] = prompt_for_color(config_name, current_value, UI_CONFIG_PROMPT_COLOR_HEX[config_name])
            elif config_name in YES_NO_CONFIGS:
                config["config_value"] = prompt_for_yes_no(config_name, current_value)
            elif config_name in NUMERIC_CONFIGS:
                config["config_value"] = prompt_for_numeric(config_name, current_value)
            elif config_name in STRING_CONFIGS:
                config["config_value"] = prompt_for_string(config_name, current_value)
        
        # [D] HANDLE SCOPES
        scopes = config.get("scopes", []) if "scopes" in config else config.get("scope", [])
        if isinstance(scopes, str):
            scopes = [scope.strip() for scope in scopes.split(",")]
        
        validated_scopes = []
        for scope in scopes:
            validated_scope = validate_scope(scope, SCOPE_MAPPING, logger=logger)
            full_scope_name = SCOPE_MAPPING.get(validated_scope, validated_scope)
            validated_scopes.append(full_scope_name)
        
        # [E] SEND TO API
        if validated_scopes:
            for full_scope_name in validated_scopes:
                send_configuration(config, api_url, full_scope_name)
        else:
            send_configuration(config, api_url)

if __name__ == "__main__":
    import sys
    print("Starting UI configurations update script (standalone mode)")
    logger.info("Starting UI configurations update script (standalone mode)")
    
    try:
        api_url = validate_url(input("Enter the full API URL (e.g., https://api.example.ucaas.tech): ").strip(), logger=logger)
        customer_name = input("Enter the customer name (e.g., sgdemo, or press Enter to skip): ").strip() or None
        logger.info(f"Customer name entered: {customer_name if customer_name else 'None'}")
        config_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join("config", "ui_configs.json")
        update_configurations(customer_name=customer_name, config_file=config_file, api_url=api_url)
        print("UI configurations update script completed")
        logger.info("UI configurations update script completed")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Script failed: {e}")
        sys.exit(1)