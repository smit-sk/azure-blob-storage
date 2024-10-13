from flask import Flask, request, redirect, url_for, render_template, send_file
from azure.storage.blob import BlobClient, ContainerClient
import os
import requests

app = Flask(__name__)

# Azure Blob Storage SAS URL (with the SAS token included)
BLOB_BASE_URL = 'https://demo9824791765.blob.core.windows.net/test-container'  # Replace with your Blob Service URL
SAS_TOKEN = 'sv=2022-11-02&ss=bf&srt=sc&sp=rwdlaciytfx&se=2024-10-13T10:52:37Z&st=2024-10-13T02:52:37Z&sip=127.0.0.1&spr=https,http&sig=P8O%2Fw5TpC7cACRrsUpjB4owpJorzIHcbUO6VJ43Ms7I%3D' 

# Azure File Share SAS URL (with the SAS token included)
FILE_SHARE_BASE_URL = 'https://demo9824791765.file.core.windows.net/p3-file-share'  # Replace with your File Share URL

# Upload to Azure Blob Storage using SAS Token
@app.route('/upload/blob', methods=['POST'])
def upload_blob():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    
    # Upload file using the BlobClient with the SAS token
    blob_url = f"{BLOB_BASE_URL}/{file.filename}?{SAS_TOKEN}"
    blob_client = BlobClient.from_blob_url(blob_url)
    
    # Upload the file data
    blob_client.upload_blob(file)
    
    return redirect(url_for('index'))

# Upload to Azure File Share using SAS Token
@app.route('/upload/file-share', methods=['POST'])
def upload_file_share():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    
    # Construct the full URL for the file
    file_url = f"{FILE_SHARE_BASE_URL}/{file.filename}?{SAS_TOKEN}"
    
    # Use requests to upload the file directly via HTTP PUT
    headers = {'x-ms-type': 'file'}
    response = requests.put(file_url, headers=headers, data=file.read())
    
    if response.status_code == 201:
        return redirect(url_for('index'))
    else:
        return f"Error uploading file: {response.text}", 500

# List Files
@app.route('/')
def index():
    # List files in Blob Storage
    container_url = f"{BLOB_BASE_URL}?{SAS_TOKEN}"
    container_client = ContainerClient.from_container_url(container_url)
    blob_files = [blob.name for blob in container_client.list_blobs()]

    # Azure File Share listing is not supported directly via SDK with SAS, but we can create a custom list of files stored locally (if mounted).
    # If not mounted, skip listing Azure Files.
    file_share_files = []

    return render_template('index.html', blob_files=blob_files, file_share_files=file_share_files)

# Download from Blob Storage
@app.route('/download/blob/<filename>')
def download_blob(filename):
    blob_url = f"{BLOB_BASE_URL}/{filename}?{SAS_TOKEN}"
    
    # Use BlobClient to download file content
    blob_client = BlobClient.from_blob_url(blob_url)
    download_file_path = f"./{filename}"
    
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    
    return send_file(download_file_path, as_attachment=True)

# Download from Azure File Share
@app.route('/download/file-share/<filename>')
def download_file_share(filename):
    file_url = f"{FILE_SHARE_BASE_URL}/{filename}?{SAS_TOKEN}"
    
    # Use requests to download the file directly
    response = requests.get(file_url)
    
    if response.status_code == 200:
        download_file_path = f"./{filename}"
        with open(download_file_path, "wb") as f:
            f.write(response.content)
        return send_file(download_file_path, as_attachment=True)
    else:
        return f"Error downloading file: {response.text}", 500

# Delete from Blob Storage
@app.route('/delete/blob/<filename>')
def delete_blob(filename):
    blob_url = f"{BLOB_BASE_URL}/{filename}?{SAS_TOKEN}"
    
    # Use BlobClient to delete the file
    blob_client = BlobClient.from_blob_url(blob_url)
    blob_client.delete_blob()
    
    return redirect(url_for('index'))

# Delete from Azure File Share
@app.route('/delete/file-share/<filename>')
def delete_file_share(filename):
    file_url = f"{FILE_SHARE_BASE_URL}/{filename}?{SAS_TOKEN}"
    
    # Use requests to delete the file directly
    response = requests.delete(file_url)
    
    if response.status_code == 202:
        return redirect(url_for('index'))
    else:
        return f"Error deleting file: {response.text}", 500

if __name__ == "__main__":
    app.run(debug=True)
