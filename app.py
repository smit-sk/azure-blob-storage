from flask import Flask, render_template, request, jsonify
from azure.storage.blob import BlobClient
import os

app = Flask(__name__)

# Azure Blob Storage configuration using full SAS URL format
AZURE_STORAGE_ACCOUNT_URL = 'https://demo9824791765.blob.core.windows.net/'
SAS_TOKEN = 'sv=2022-11-02&ss=bf&srt=sc&sp=rwdlaciytfx&se=2024-10-13T23:00:51Z&st=2024-10-13T15:00:51Z&sip=127.0.0.1&spr=https,http&sig=3BuhM9q3XHlhq48lqPQ9q6ibKBs1BzskZ0dYBRZ4nXo%3D'
BLOB_CONTAINER_NAME = 'test-container'

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Check if the app is running in Azure
            if os.environ.get('AZURE_ENVIRONMENT') == 'true':
                file_path = os.path.join('/home/site/wwwroot/share', file.filename)  # Azure mounted path
            else:
                # Use a temporary path for local development
                file_path = os.path.join(os.getcwd(), 'uploads', file.filename)  # Local path
            
            # Ensure the local uploads directory exists
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            # Save the file
            file.save(file_path)

            return jsonify(message="File uploaded to Azure Files successfully!"), 200

    return jsonify(message="No file uploaded."), 400


if __name__ == '__main__':
    app.run(debug=True)
