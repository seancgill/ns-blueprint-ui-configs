import streamlit as st
import pandas as pd
import json
import os
import time
import requests
from utils.api_helper import APIHelper

# --- 1. CONFIGURATION CONSTANTS ---
CONFIG_PATH = os.path.join("config", "ui_configs.json")
FIXED_CLIENT_ID = "configsapp"

SCOPE_MAPPING = {
    "su": "Super User", "res": "Reseller", "om": "Office Manager",
    "adv": "Advanced User", "cca": "Call Center Agent", "ccs": "Call Center Supervisor"
}

# --- NEW CONSTANT: HELP TEXT MAPPING ---
CONFIG_HELP_TEXT = {
    "MOBILE_REGISTRATION_SERVER": 'Example : "_sip._tls.core1-ord.xyzcompany.net:5061"',
    "PORTAL_USERS_SECURE_PASSWORD_MIN_LENGTH": "Minimum for user portal login password",
    "PORTAL_USERS_SECURE_PASSWORD_MIN_CAPITAL_LETTER_COUNT": "Minimum for user portal login password",
    "PORTAL_USERS_SECURE_PASSWORD_MIN_NUMBER_COUNT": "Minimum for user portal login password",
    "PORTAL_USERS_SECURE_PASSWORD_MIN_SPECIAL_CHAR_COUNT": "Minimum for user portal login password",
    "PORTAL_USERS_MIN_PASSWORD_LENGTH": "Minimum for user portal created voicemail pin",
    "PORTAL_USERS_CALLERID_USE_DROPDOWN_DID_LIST": "User profile CID limited to #'s in inventory, otherwise freeform",
    "PORTAL_LOGGED_IN_POWERED_BY": "Small text bottom of portal, typically copyright info branding",
    "PORTAL_THREE_WAY_CALL_DISCONNECT_OTHERS_ON_END": "Webphone behavior, when originator ends 3-way call",
    "EMAIL_HTML_GET_SUPPORT_LINK": "Support link used in email footers"
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
    "MOBILE_REGISTRATION_SERVER"
]

# --- 2. AUTHENTICATION ---
def authenticate(api_url, client_secret, username, password):
    clean_url = api_url.replace("https://", "").replace("http://", "").strip("/")
    token_url = f"https://{clean_url}/ns-api/oauth2/token/"
    payload = {
        "grant_type": "password",
        "client_id": FIXED_CLIENT_ID,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    try:
        response = requests.post(token_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json(), clean_url
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None, None

# --- UPDATED LOADER LOGIC ---
def load_blueprint_config(customer_name=None):
    """Loads JSON and performs the 'custID' replacement if a customer name is provided."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            configs = json.load(f)
            
        if not isinstance(configs, list):
            st.error(f"Configuration file {CONFIG_PATH} must contain a JSON array.")
            return []

        # Perform the logic from your validators file
        processed_configs = []
        for config in configs:
            if not isinstance(config, dict) or "config_name" not in config or "config_value" not in config:
                continue # Skip malformed entries
            
            # THE REPLACEMENT LOGIC
            if customer_name and isinstance(config.get("config_value"), str):
                config["config_value"] = config["config_value"].replace("custID", customer_name)
            
            processed_configs.append(config)
            
        return processed_configs

    except FileNotFoundError:
        st.error(f"Config file not found at {CONFIG_PATH}")
        return []
    except json.JSONDecodeError:
        st.error(f"Invalid JSON in {CONFIG_PATH}")
        return []

# --- 3. MAIN EXECUTION LOGIC ---

def run_execution_engine():
    st.title("🚀 NS-Blueprint-UI_Configs")

    # Initialize Session State
    if 'execution_queue' not in st.session_state:
        st.session_state['execution_queue'] = []
    if 'current_step_index' not in st.session_state:
        st.session_state['current_step_index'] = 0
    if 'execution_log' not in st.session_state:
        st.session_state['execution_log'] = []
    if 'app_phase' not in st.session_state:
        st.session_state['app_phase'] = "SETUP"

    # --- TOP COMPONENT: LIVE LOG ---
    with st.expander("📡 Live API Transaction Log", expanded=True):
        if st.session_state['execution_log']:
            st.dataframe(pd.DataFrame(st.session_state['execution_log']), use_container_width=True, hide_index=True)
        else:
            st.info("Waiting to start...")

    # --- PHASE 1: SETUP (THE GATEKEEPERS) ---
    if st.session_state['app_phase'] == "SETUP":
        st.header("1. Configuration Setup")
        
        with st.form("setup_form"):
            st.subheader("Gatekeeper Questions")
            
            # --- NEW: CUSTOMER NAME INPUT ---
            cust_name_input = st.text_input(
                "Customer Name (Required for 'custID' replacement)", 
                help="This replaces occurrences of 'custID' in the config values (e.g., 'sgdemo')."
            )
            
            st.markdown("---")
            
            # Question 1: Resellers
            include_resellers = st.radio(
                "Do you want to apply Reseller-specific configs?",
                ("No", "Yes"), index=0
            )
            
            # Question 2: CSS Colors
            include_css = st.radio(
                "Do you want to set/change CSS color configurations?",
                ("No", "Yes"), index=0
            )
            
            submitted = st.form_submit_button("Start Execution")
            
            if submitted:
                # Validate Customer Name if it might be needed
                # (You can make this optional if you prefer, but usually it's safer to require it)
                if not cust_name_input:
                     st.warning("⚠️ Please enter a Customer Name.")
                else:
                    # LOAD AND PROCESS CONFIGS with the Name
                    raw_configs = load_blueprint_config(customer_name=cust_name_input)
                    
                    filtered_queue = []
                    
                    for config in raw_configs:
                        # Filter 1: Resellers
                        if "reseller" in config and include_resellers == "No":
                            continue
                        
                        # Filter 2: CSS Colors
                        if config["config_name"] in UI_CONFIG_PROMPT_COLOR_HEX and include_css == "No":
                            continue
                            
                        filtered_queue.append(config)
                    
                    if not filtered_queue:
                        st.error("No configurations selected based on your choices.")
                    else:
                        st.session_state['execution_queue'] = filtered_queue
                        st.session_state['app_phase'] = "RUNNING"
                        st.session_state['current_step_index'] = 0
                        st.rerun()

    # --- PHASE 2: RUNNING (THE LOOP) ---
    elif st.session_state['app_phase'] == "RUNNING":
        process_queue()

    # --- PHASE 3: FINISHED ---
    elif st.session_state['app_phase'] == "FINISHED":
        st.success("✅ All configurations completed!")
        if st.button("Start Over"):
            st.session_state['app_phase'] = "SETUP"
            st.session_state['execution_log'] = []
            st.rerun()

def process_queue():
    queue = st.session_state['execution_queue']
    index = st.session_state['current_step_index']

    if index >= len(queue):
        st.session_state['app_phase'] = "FINISHED"
        st.rerun()
        return

    current_item = queue[index]
    config_name = current_item["config_name"]
    
    is_reseller = "reseller" in current_item
    
    needs_input = False
    if not is_reseller:
        if config_name in UI_CONFIG_PROMPT_COLOR_HEX: needs_input = True
        elif config_name in YES_NO_CONFIGS: needs_input = True
        elif config_name in NUMERIC_CONFIGS: needs_input = True
        elif config_name in STRING_CONFIGS: needs_input = True

    st.markdown(f"### Step {index + 1}/{len(queue)}: `{config_name}`")
    
    if needs_input:
        render_input_form(current_item)
    else:
        with st.spinner(f"Applying {config_name}..."):
            execute_api_call(current_item, current_item.get("config_value"))
        st.session_state['current_step_index'] += 1
        time.sleep(0.2) 
        st.rerun()

def render_input_form(item):
    name = item["config_name"]
    default_val = item.get("config_value", "")
    
    # 1. Look up help text (returns None if not found, which is fine)
    help_tooltip = CONFIG_HELP_TEXT.get(name, None)
    
    with st.form(key=f"step_{st.session_state['current_step_index']}"):
        user_val = default_val 
        
        # Color Picker (No help text usually needed, but can be added if defined)
        if name in UI_CONFIG_PROMPT_COLOR_HEX:
            st.info(f"🎨 **Color Config**: {UI_CONFIG_PROMPT_COLOR_HEX[name]}")
            safe_color = default_val if str(default_val).startswith("#") else "#000000"
            user_val = st.color_picker(f"Select color for {name}", safe_color, help=help_tooltip)
            
        # Radio Buttons
        elif name in YES_NO_CONFIGS:
            idx = 0 if str(default_val).lower() == "yes" else 1
            user_val = st.radio(f"Set {name}", ["yes", "no"], index=idx, help=help_tooltip)
            
        # Numeric Inputs
        elif name in NUMERIC_CONFIGS:
            user_val = st.number_input(
                f"Set value for {name}", 
                value=int(default_val) if str(default_val).isdigit() else 0,
                help=help_tooltip
            )
            
        # Text Inputs
        elif name in STRING_CONFIGS:
            user_val = st.text_input(f"Enter value for {name}", value=default_val, help=help_tooltip)

        if st.form_submit_button("Submit & Apply"):
            execute_api_call(item, user_val)
            st.session_state['current_step_index'] += 1
            st.rerun()

def execute_api_call(item, final_value):
    api = APIHelper(st.session_state['api_url'], st.session_state['access_token'])
    
    scopes = item.get("scopes", item.get("scope", []))
    if isinstance(scopes, str):
        scopes = [s.strip() for s in scopes.split(",")]
    
    validated_scopes = [SCOPE_MAPPING.get(s, s) for s in scopes]
    
    payload = {
        "config-name": item["config_name"],
        "config-value": str(final_value),
        "admin-ui-account-type": "*",
        "reseller": item.get("reseller", "*"),
        "user": "*",
        "domain": "*",
        "description": "Updated via Streamlit App"
    }

    targets = validated_scopes if validated_scopes else ["*"]
    
    for scope in targets:
        payload["user-scope"] = scope
        try:
            # Attempt POST
            resp = api.post("ns-api/v2/configurations", payload)
            
            # --- STATUS CODE LOGIC ---
            if resp.ok:
                if resp.status_code == 202:
                    status = "✅ Updated : 202"
                elif resp.status_code == 201:
                    status = "✅ Created : 201"
                else:
                    status = f"✅ Success : {resp.status_code}"
            else:
                status = f"❌ {resp.status_code}"
            
            # Handle 409 Conflict -> Try PUT
            if resp.status_code == 409:
                resp = api.put("ns-api/v2/configurations", payload)
                
                # Update status for the PUT attempt
                if resp.ok:
                    if resp.status_code == 202:
                        status = "✅ Updated : 202"
                    else:
                        status = f"✅ Updated : {resp.status_code}"
                else:
                    status = f"❌ {resp.status_code}"
                
        except Exception as e:
            status = f"❌ Error: {str(e)}"

        log_entry = {
            "Status": status,
            "Config": item["config_name"],
            "Value": str(final_value),
            "Scope": scope
        }
        st.session_state['execution_log'].insert(0, log_entry)
        
# --- LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    
    # 1. CREATE COLUMNS TO CENTER EVERYTHING
    # The middle column (2) is where the content goes. The sides (1) are empty spacers.
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 2. ICON & HEADER
        # Create sub-columns just to center the image perfectly
        sub_c1, sub_c2, sub_c3 = st.columns([1, 1, 1])
        with sub_c2:
            st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=100)
        
        # Use HTML to center the text
        st.markdown("<h2 style='text-align: center;'>NS-Blueprint Login</h2>", unsafe_allow_html=True)
        
        # 3. LOGIN FORM
        with st.form("login"):
            # READ-ONLY CLIENT ID FIELD
            st.text_input(
                "OAuth Client ID", 
                value=FIXED_CLIENT_ID, 
                disabled=True, 
                help="⚠️ IMPORTANT: You must login to the target NetSapiens cluster as Super User and create this OAuth Client ID ('configsapp') before attempting to connect."
            )

            # STANDARD INPUTS
            api_url = st.text_input("API URL", "api.netsapiens.com")
            secret = st.text_input("Client Secret", type="password", help="The secret generated when you created the 'configsapp' client.")
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            
            # Button with 'use_container_width=True' to make it span the full form width
            if st.form_submit_button("Connect", use_container_width=True):
                data, valid_url = authenticate(api_url, secret, user, pwd)
                if data:
                    st.session_state['authenticated'] = True
                    st.session_state['access_token'] = data['access_token']
                    st.session_state['api_url'] = valid_url
                    st.rerun()
else:
    run_execution_engine()