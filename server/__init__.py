import json
import os
from flask import Flask, render_template, request, jsonify, session
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


def parentFilePath(filepath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_path = os.path.abspath(os.path.join(script_dir, os.pardir))
    updated_path = os.path.join(parent_path, filepath)
    return updated_path


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

ScopesMap = {key.title().replace("_", ""): value for key, value in Scopes.__dict__.items() if not key.startswith('_') and not callable(value)}

@app.route('/')
def index():
    # Clear the session to ensure a fresh start
    session.clear()
    # Create a dictionary mapping scope names to their enum values
    return render_template('index.html', Scopes=ScopesMap.keys())

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    environment = data.get('environment')
    client_id = data.get('clientId')
    client_secret = data.get('clientSecret')
    scopes = data.get('scopes')

    # Create or retrieve the auth_client from the session
    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        environment=environment,
        redirect_uri='http://localhost:54321/process_data',
    )

    authorization_url = auth_client.get_authorization_url([ScopesMap[s] for s in scopes])
    session['auth_client_data'] = dict(
        client_id=client_id,
        client_secret=client_secret,
        environment=environment,
        redirect_uri='http://localhost:54321/process_data'
    )

    # Return the authorization URL as a response
    return authorization_url

@app.route('/process_data', methods=['GET'])
def process_data():
    realm_id = request.args.get('realmId')
    authorization_code = request.args.get('code')
    state = request.args.get('state')

    if realm_id is None or authorization_code is None:
        return 'Missing parameters', 400

    # Retrieve the auth_client from the session
    auth_client_data = session.get('auth_client_data')

    if auth_client_data is None:
        return 'Authentication client not found in session', 401

    # Process the data here (e.g., authenticate the authorization code)    
    auth_client = AuthClient(
    **auth_client_data
    )
    try:
        auth_client.get_bearer_token(authorization_code, realm_id)
        data = {
            **session['auth_client_data'],
            "refresh_token": auth_client.refresh_token,
            "realm_id": realm_id
        }
        
        with open(parentFilePath("data.json"), "w") as f:
            json.dump(data, f)

        return f'Authorization successful \n{data}'
    except Exception as e:
        return f'Authorization failed {e}', 401

if __name__ == '__main__':
    app.run(port=54321)
