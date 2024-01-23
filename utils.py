import requests

# Function to get a new access token
def get_access_token():
    token_url = 'your_url_to_get_token'
    payload = {"code": "your_authorization_code"}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(token_url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        raise Exception(f"Failed to obtain token: {response.status_code} {response.text}")
    

def request_chat_api(access_token, chat_payload):
    chat_url = 'your_url_of_base_api'
    chat_headers = {'Authorization': access_token}

    chat_response = requests.post(chat_url, json=chat_payload, headers=chat_headers, verify=False)
    if chat_response.status_code == 200:
        return chat_response.json()
    else:
        # If the token has expired, obtain a new token and retry the request once more
        if chat_response.json().get('errorCode') == 401:
            print("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            chat_headers['Authorization'] = new_access_token
            chat_response = requests.post(chat_url, json=chat_payload, headers=chat_headers, verify=False)
            if chat_response.status_code == 200:
                return chat_response.json()
            else:
                raise Exception(f"Failed on retry with new token: {chat_response.status_code} {chat_response.text}")
        else:
            raise Exception(f"Failed to call chat API: {chat_response.status_code} {chat_response.text}")
        

def request_embedding(access_token, embedding_param):
    embedding_url="your_url_of_base_api"
    embedding_header = {'Authorization': access_token}
    embedding_response = requests.post(embedding_url, json=embedding_param, headers=embedding_header, verify=False)
    if embedding_response.status_code == 200:
        return embedding_response.json()
    else:
        # If the token has expired, obtain a new token and retry the request once more
        if embedding_response.json().get('errorCode') == 401:
            print("Token expired, fetching a new token...")
            new_access_token = get_access_token()
            embedding_response['Authorization'] = new_access_token
            embedding_response = requests.post(embedding_url, json=embedding_param, headers=embedding_header, verify=False)
            if embedding_response.status_code == 200:
                return embedding_response.json()
            else:
                raise Exception(f"Failed on retry with new token: {embedding_response.status_code} {embedding_response.text}")
        else:
            raise Exception(f"Failed to call chat API: {embedding_response.status_code} {embedding_response.text}")