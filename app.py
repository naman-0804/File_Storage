from flask import Flask, request, render_template, jsonify, send_file, flash, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import io
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# Config
FOLDER_ID = '1g7K6oqInxwaiZ_LoJ5QSRtKBUCgS5b_3'
SCOPES = ['https://www.googleapis.com/auth/drive']

import tempfile
import json

# Load credentials from environment variable
creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not creds_json:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set")

with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_cred:
    temp_cred.write(creds_json)
    temp_cred.flush()
    SERVICE_ACCOUNT_FILE = temp_cred.name

# Use this temporary file for credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)
def upload_to_drive(file_path, file_name):
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')  # Return the file ID

def delete_file(file_id):
    drive_service.files().delete(fileId=file_id).execute()

@app.route('/delete/<file_id>', methods=['POST'])
def delete(file_id):
    try:
        delete_file(file_id)
        flash('File deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
    return redirect('/')

def list_files():
    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return send_file(fh, as_attachment=True, download_name=file_name)

@app.route('/')
def index():
    files = list_files()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        # Get all files instead of just one
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        uploaded_count = 0
        os.makedirs('uploads', exist_ok=True)
        
        file_ids = []
        for file in files:
            if file and file.filename != '':
                filepath = os.path.join('uploads', file.filename)
                file.save(filepath)
                file_id = upload_to_drive(filepath, file.filename)
                file_ids.append(file_id)
                os.remove(filepath)
                uploaded_count += 1
        
        message = 'File uploaded successfully' if uploaded_count == 1 else f'{uploaded_count} files uploaded successfully'
        return jsonify({
            'success': True, 
            'message': message,
            'count': uploaded_count,
            'file_ids': file_ids
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    try:
        file_ids = request.json.get('file_ids', [])
        if not file_ids:
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        
        deleted_count = 0
        errors = []
        
        for file_id in file_ids:
            try:
                delete_file(file_id)
                deleted_count += 1
            except Exception as e:
                errors.append(f"Error deleting file {file_id}: {str(e)}")
        
        if errors:
            if deleted_count > 0:
                flash(f'Deleted {deleted_count} files. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Failed to delete files: {"; ".join(errors)}', 'error')
        else:
            message = 'File deleted successfully' if deleted_count == 1 else f'{deleted_count} files deleted successfully'
            flash(message, 'success')
            
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'errors': errors
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<file_id>/<file_name>')
def download(file_id, file_name):
    return download_file(file_id, file_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
