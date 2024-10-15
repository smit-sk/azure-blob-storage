from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from azure.storage.blob import BlobClient
import msal
import os
#test email - chrisgreen@smitkhokhariyaoutlook.onmicrosoft.com
app = Flask(__name__)
app = Flask(__name__)
app.secret_key = 'main-secret-key'  # Replace with a real secret key

# Microsoft OAuth settings
CLIENT_ID = '678cd6ec-3584-44d9-8cf8-f87c4a28b193'
CLIENT_SECRET = '5Rl8Q~ck~adAeoCXgNzHhDk1npNZ31MGJmjpVbZh'
AUTHORITY = 'https://login.microsoftonline.com/ce262059-46ac-47aa-82bb-7dcf70acd5c1'
SCOPES = ['User.Read']
REDIRECT_PATH = '/getAToken'

@app.route('/')
def index():
    user = session.get('user')
    email = user.get('preferred_username') if user else None
    role = session.get('roles')
    return render_template('upload.html', email=email, user=user, role=role)

@app.route('/login')
def login():
    auth_url = _build_msal_app().get_authorization_request_url(
        SCOPES,
        redirect_uri='https://p3-e4bab8g7b2dmfjbd.canadacentral-01.azurewebsites.net/getAToken'
    )
    return redirect(auth_url)

def user_has_role(required_role):
    user_roles = session.get('roles', [])
    return required_role in user_roles

@app.route(REDIRECT_PATH)
def authorized():
    result = _build_msal_app().acquire_token_by_authorization_code(
        request.args['code'],
        scopes=SCOPES,
        redirect_uri='https://p3-e4bab8g7b2dmfjbd.canadacentral-01.azurewebsites.net/getAToken'
    )
    if 'error' in result:
        return f"Login failed: {result['error']}"
    
    # Save the token and claims in session
    session['user'] = result.get('id_token_claims')
    session['access_token'] = result.get('access_token')
    
    # Check if roles or groups are present in the token claims
    session['roles'] = session['user'].get('roles', [])
    session['groups'] = session['user'].get('groups', [])  # Groups if roles are missing

    print("Roles:", session.get('roles'))
    print("Groups:", session.get('groups'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"{AUTHORITY}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={url_for('index', _external=True)}"
    )

def _build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY,
        client_credential=CLIENT_SECRET)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not user_has_role('Storage Blob Data Contributor'):
        return jsonify(message="Unauthorized: You do not have permission to upload files."), 403
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Create a BlobClient using the full SAS URL for the blob (file)
            blob_client = BlobClient.from_blob_url(
                blob_url=f"https://demo9824791765.blob.core.windows.net/test-container/{file.filename}?sp=rcw&st=2024-10-13T15:39:23Z&se=2024-10-13T23:39:23Z&sv=2022-11-02&sr=c&sig=ETP3Dp%2BnJgUDBVP9rrAM6A%2F1fj7hyoFot8Qv543WuPg%3D"
            )
            
            # Upload the file to Azure Blob Storage
            blob_client.upload_blob(file, overwrite=True)

            # Return a JSON response with a success message
            return jsonify(message="File uploaded successfully!"), 200

    return jsonify(message="No file uploaded."), 400

@app.route('/upload_to_files', methods=['POST'])
def upload_to_files():
    if not user_has_role('Storage File Data Contributor'):
        return jsonify(message="Unauthorized: You do not have permission to upload to Azure Files."), 403
    
    if 'file' not in request.files:
        return jsonify(message="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(message="No selected file"), 400

    if file:
        try:
            # First, try to save to the Azure File Share path
            azure_path = '/share'
            file_path = os.path.join(azure_path, file.filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Attempt to save the file
            file.save(file_path)
            
            return jsonify(message="File uploaded successfully to Azure File Share!"), 200
        
        except Exception as azure_error:
            
            try:
                # Fallback to local storage
                local_path = os.path.join(os.getcwd(), 'uploads')
                file_path = os.path.join(local_path, file.filename)
                
                # Ensure the local directory exists
                os.makedirs(local_path, exist_ok=True)
                
                # Save to local path
                file.save(file_path)
                
                return jsonify(message="File uploaded successfully to local storage!"), 200
            
            except Exception as local_error:
                
                return jsonify(message=f"Failed to upload file: {str(local_error)}"), 500

    return jsonify(message="Invalid file"), 400

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        # List all files and directories in the mounted Azure File Share
        files_and_folders = []
        
        for root, dirs, files in os.walk('/share'):
            for directory in dirs:
                files_and_folders.append(f"Directory: {os.path.join(root, directory)}")
            for file in files:
                files_and_folders.append(f"File: {os.path.join(root, file)}")
        
        # Return the list as a JSON response
        return jsonify(files_and_folders=files_and_folders), 200
    except Exception as e:
        return jsonify(message=f"Error listing files: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)
