import os
import requests
import json
from typing import Dict, Any, Optional, Union
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
TOKEN_URL = os.getenv('TOKEN_URL', 'your_url_to_get_token')
CHAT_API_URL = os.getenv('CHAT_API_URL', 'your_url_of_base_api')
EMBEDDING_API_URL = os.getenv('EMBEDDING_API_URL', 'your_url_of_base_api')
AUTH_CODE = os.getenv('AUTH_CODE', 'your_authorization_code')
VERIFY_SSL = os.getenv('VERIFY_SSL', 'False').lower() in ('true', '1', 't')

# Function to get a new access token
def get_access_token():
    """Get a new access token from the API"""
    try:
        payload = {"code": AUTH_CODE}
        headers = {'Content-Type': 'application/json'}

        logger.debug(f"Requesting token from {TOKEN_URL}")
        response = requests.post(TOKEN_URL, json=payload, headers=headers, verify=VERIFY_SSL, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        if 'data' in token_data and 'access_token' in token_data['data']:
            logger.info("Token obtained successfully")
            return token_data['data']['access_token']
        else:
            logger.error(f"Token response structure unexpected: {token_data}")
            raise KeyError("Expected 'data.access_token' in response")
    except requests.RequestException as e:
        logger.error(f"Token request failed: {str(e)}")
        raise Exception(f"Failed to obtain token: {str(e)}")
    

def request_chat_api(access_token: str, chat_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to the chat API with retries for token expiration"""
    chat_headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    
    try:
        logger.debug(f"Sending chat request to {CHAT_API_URL}")
        chat_response = requests.post(
            CHAT_API_URL, 
            json=chat_payload, 
            headers=chat_headers, 
            verify=VERIFY_SSL,
            timeout=30
        )
        
        # Check for successful response
        if chat_response.status_code == 200:
            return chat_response.json()
            
        # Handle token expiration
        response_data = chat_response.json()
        if response_data.get('errorCode') == 401:
            logger.warning("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            chat_headers['Authorization'] = new_access_token
            
            # Retry with new token
            retry_response = requests.post(
                CHAT_API_URL, 
                json=chat_payload, 
                headers=chat_headers, 
                verify=VERIFY_SSL,
                timeout=30
            )
            
            if retry_response.status_code == 200:
                return retry_response.json()
            else:
                logger.error(f"Retry failed: {retry_response.status_code} {retry_response.text}")
                raise Exception(f"Failed on retry with new token: {retry_response.status_code} {retry_response.text}")
        else:
            logger.error(f"Chat API request failed: {chat_response.status_code} {chat_response.text}")
            raise Exception(f"Failed to call chat API: {chat_response.status_code} {chat_response.text}")
            
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Network error calling chat API: {str(e)}")
        

def request_embedding(access_token: str, embedding_param: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to the embedding API with retries for token expiration"""
    embedding_header = {'Authorization': access_token, 'Content-Type': 'application/json'}
    
    try:
        logger.debug(f"Sending embedding request to {EMBEDDING_API_URL}")
        embedding_response = requests.post(
            EMBEDDING_API_URL, 
            json=embedding_param, 
            headers=embedding_header, 
            verify=VERIFY_SSL,
            timeout=10
        )
        
        # Check for successful response
        if embedding_response.status_code == 200:
            return embedding_response.json()
            
        # Handle token expiration
        response_data = embedding_response.json()
        if response_data.get('errorCode') == 401:
            logger.warning("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            embedding_header['Authorization'] = new_access_token
            
            # Retry with new token
            retry_response = requests.post(
                EMBEDDING_API_URL, 
                json=embedding_param, 
                headers=embedding_header, 
                verify=VERIFY_SSL,
                timeout=10
            )
            
            if retry_response.status_code == 200:
                return retry_response.json()
            else:
                logger.error(f"Retry failed: {retry_response.status_code} {retry_response.text}")
                raise Exception(f"Failed on retry with new token: {retry_response.status_code} {retry_response.text}")
        else:
            logger.error(f"Embedding API request failed: {embedding_response.status_code} {embedding_response.text}")
            raise Exception(f"Failed to call embedding API: {embedding_response.status_code} {embedding_response.text}")
            
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Network error calling embedding API: {str(e)}")