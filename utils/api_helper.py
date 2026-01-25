import requests
import json
# We can keep your existing logging setup if you copy the 'utils' folder
# If not, you can replace this with standard 'import logging'
try:
    from utils.logging_setup import setup_logging
except ImportError:
    import logging
    def setup_logging():
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("APIHelper")

class APIHelper:
    def __init__(self, api_url, access_token, logger=None):
        """
        Initializes the API helper with a dynamic URL and OAuth token from the user session.
        
        Args:
            api_url (str): The customer's API domain (e.g., 'api.customer.com').
            access_token (str): The Bearer token obtained during login.
            logger (logging.Logger, optional): Custom logger. Defaults to setup_logging().
        """
        # 1. Sanitize the URL (Ensure https:// exists and no trailing slash)
        api_url = api_url.strip()
        if not api_url.startswith("http"):
            self.api_url = f"https://{api_url}".rstrip('/')
        else:
            self.api_url = api_url.rstrip('/')

        # 2. Setup Logging
        self.logger = logger if logger else setup_logging()
        
        # 3. Set Headers with the Dynamic Token
        if not access_token:
            raise ValueError("APIHelper initialized without a valid access_token!")

        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Log initialization (Masking the token for security)
        token_preview = access_token[:10] + "..." if len(access_token) > 10 else "******"
        self.logger.info(f"APIHelper initialized for target: {self.api_url}")
        self.logger.debug(f"Using Token: {token_preview}")

    def post(self, endpoint, data, files=None, timeout=30):
        url = f"{self.api_url}/{endpoint}"
        self.logger.info(f"Making POST request to {url}")
        
        # Only log payload if it's not a file upload (too noisy/binary)
        if not files:
            self.logger.debug(f"Request payload: {json.dumps(data, indent=2)}")
            
        try:
            # Use data=json.dumps(data) for JSON, or data=data for files/form-data
            response = requests.post(
                url, 
                headers=self.headers, 
                data=json.dumps(data) if not files else data, 
                files=files, 
                timeout=timeout
            )
            self.logger.info(f"Received response with status code: {response.status_code}")
            
            # Log error text if request failed, otherwise debug
            if not response.ok:
                self.logger.error(f"Failed Response: {response.text}")
            else:
                self.logger.debug(f"Response text: {response.text}")
                
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling {url}: {e}")
            raise

    def put(self, endpoint, data, files=None, timeout=30):
        url = f"{self.api_url}/{endpoint}"
        self.logger.info(f"Making PUT request to {url}")
        if not files:
            self.logger.debug(f"Request payload: {json.dumps(data, indent=2)}")
        try:
            response = requests.put(
                url, 
                headers=self.headers, 
                data=json.dumps(data) if not files else data, 
                files=files, 
                timeout=timeout
            )
            self.logger.info(f"Received response with status code: {response.status_code}")
            
            if not response.ok:
                self.logger.error(f"Failed Response: {response.text}")
            else:
                self.logger.debug(f"Response text: {response.text}")
                
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling {url}: {e}")
            raise

    def get(self, endpoint, timeout=30):
        url = f"{self.api_url}/{endpoint}"
        self.logger.info(f"Making GET request to {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            self.logger.info(f"Received response with status code: {response.status_code}")
            self.logger.debug(f"Response text: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling {url}: {e}")
            raise

    def delete(self, endpoint, timeout=30):
        url = f"{self.api_url}/{endpoint}"
        self.logger.info(f"Making DELETE request to {url}")
        try:
            response = requests.delete(url, headers=self.headers, timeout=timeout)
            self.logger.info(f"Received response with status code: {response.status_code}")
            self.logger.debug(f"Response text: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling {url}: {e}")
            raise