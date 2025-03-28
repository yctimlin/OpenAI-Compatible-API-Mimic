"""
API utilities for the OpenAI-Compatible API.

This module provides utilities for interacting with the actual OpenAI API 
or any other compatible API endpoint, handling authentication, requests
and error handling.
"""

import json
import requests
from typing import Dict, Any, Optional
from loguru import logger

from src.config.settings import settings


def get_access_token() -> str:
    """
    Get a new access token from the API.
    
    Returns:
        str: The access token string.
        
    Raises:
        Exception: If token request fails.
    """
    try:
        payload = {"code": settings.AUTH_CODE}
        headers = {'Content-Type': 'application/json'}

        logger.debug(f"Requesting token from {settings.TOKEN_URL}")
        response = requests.post(
            settings.TOKEN_URL, 
            json=payload, 
            headers=headers, 
            verify=settings.VERIFY_SSL,
            timeout=10
        )
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
    """
    Make a request to the chat API with retries for token expiration.
    
    Args:
        access_token (str): The access token for authentication.
        chat_payload (Dict[str, Any]): The payload to send to the chat API.
        
    Returns:
        Dict[str, Any]: The response from the chat API.
        
    Raises:
        Exception: If the API request fails.
    """
    chat_headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    
    try:
        logger.debug(f"Sending chat request to {settings.CHAT_API_URL}")
        logger.debug(f"Chat payload: {json.dumps(chat_payload, indent=2)}")
        
        chat_response = requests.post(
            settings.CHAT_API_URL, 
            json=chat_payload, 
            headers=chat_headers, 
            verify=settings.VERIFY_SSL,
            timeout=30
        )
        
        # Check for successful response
        if chat_response.status_code == 200:
            logger.debug("Chat request successful")
            return chat_response.json()
            
        # Handle token expiration
        response_data = chat_response.json()
        if response_data.get('errorCode') == 401:
            logger.warning("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            chat_headers['Authorization'] = new_access_token
            
            # Retry with new token
            retry_response = requests.post(
                settings.CHAT_API_URL, 
                json=chat_payload, 
                headers=chat_headers, 
                verify=settings.VERIFY_SSL,
                timeout=30
            )
            
            if retry_response.status_code == 200:
                logger.debug("Chat retry request successful")
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
    """
    Make a request to the embedding API with retries for token expiration.
    
    Args:
        access_token (str): The access token for authentication.
        embedding_param (Dict[str, Any]): The parameters for the embedding request.
        
    Returns:
        Dict[str, Any]: The response from the embedding API.
        
    Raises:
        Exception: If the API request fails.
    """
    embedding_header = {'Authorization': access_token, 'Content-Type': 'application/json'}
    
    try:
        logger.debug(f"Sending embedding request to {settings.EMBEDDING_API_URL}")
        logger.debug(f"Embedding parameters: {json.dumps(embedding_param, indent=2)}")
        
        embedding_response = requests.post(
            settings.EMBEDDING_API_URL, 
            json=embedding_param, 
            headers=embedding_header, 
            verify=settings.VERIFY_SSL,
            timeout=10
        )
        
        # Check for successful response
        if embedding_response.status_code == 200:
            logger.debug("Embedding request successful")
            return embedding_response.json()
            
        # Handle token expiration
        response_data = embedding_response.json()
        if response_data.get('errorCode') == 401:
            logger.warning("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            embedding_header['Authorization'] = new_access_token
            
            # Retry with new token
            retry_response = requests.post(
                settings.EMBEDDING_API_URL, 
                json=embedding_param, 
                headers=embedding_header, 
                verify=settings.VERIFY_SSL,
                timeout=10
            )
            
            if retry_response.status_code == 200:
                logger.debug("Embedding retry request successful")
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