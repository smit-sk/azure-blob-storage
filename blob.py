import os
import random
import string
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient

app = Flask(__name__, instance_relative_config=True)

# Load configurations

account = 'demo9824791765'  # Your Azure account name
key="access-key"
container = 'test-container'  # Your container name

# Create BlobServiceClient instance
blob_service_client = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net", credential=key)
container_client = blob_service_client.get_container_client(container)

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload New File</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                color: #333;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            input[type="file"] {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ddd;
                width: 100%;
                max-width: 300px;
            }
            input[type="submit"] {
                padding: 10px 20px;
                background-color: #5cb85c;
                border: none;
                color: white;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            input[type="submit"]:hover {
                background-color: #4cae4c;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload New File</h1>
            <form action="" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <input type="submit" value="Upload">
            </form>
        </div>
    </body>
    </html>
    '''

def result_page(ref):
    return f'''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Link</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            h1 {{
                color: #333;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin-top: 20px;
            }}
            a {{
                display: inline-block;
                margin-top: 15px;
                text-decoration: none;
                color: #5cb85c;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Uploaded File Link</h1>
            <p>{ref}</p>
            <img src="{ref}">
            <a href="/">Upload another file</a>
        </div>
    </body>
    </html>
    '''

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    app.run(debug=True)
