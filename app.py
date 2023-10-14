import os
import csv
from flask import Flask, request, redirect, render_template, url_for
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'static/tutorials'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/tutorial', methods=['GET', 'POST'])
def upload_file():
    files = []
    if os.path.exists('pdf_descriptions.csv'):
        with open('pdf_descriptions.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                filename, description = row
                file_url = url_for('static', filename=f"tutorials/{filename}")
                files.append({'name': filename, 'url': file_url, 'description': description})

    links = []
    if os.path.exists('links.txt'):
        with open('links.txt', 'r') as file:
            for line in file:
                link, description = line.strip().split('|')
                links.append({'link': link, 'description': description})

    return render_template('index.html', files=files, links=links)

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' in request.files:
        file = request.files['file']
        description = request.form.get('pdf_description', '')
        if file.filename != '' and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open('pdf_descriptions.csv', 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([filename, description])
    return redirect(url_for('upload_file'))

@app.route('/submit-link', methods=['POST'])
def submit_link():
    link = request.form.get('link')
    description = request.form.get('link_description', '')
    if link:
        with open('links.txt', 'a') as file:
            file.write(link + '|' + description + '\n')
    return redirect(url_for('upload_file'))

@app.route('/delete/pdf/<filename>', methods=['GET'])
def delete_pdf(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if os.path.exists('pdf_descriptions.csv'):
            with open('pdf_descriptions.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                rows = [row for row in reader]

            with open('pdf_descriptions.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row in rows:
                    if row[0] != filename:
                        writer.writerow(row)

        return redirect(url_for('upload_file'))
    except Exception as e:
        print(str(e))
        return str(e), 500

@app.route('/delete/link/<int:index>', methods=['GET'])
def delete_link(index):
    try:
        if os.path.exists('links.txt'):
            with open('links.txt', 'r') as file:
                lines = file.readlines()

            if 0 <= index < len(lines):
                del lines[index]

            with open('links.txt', 'w') as file:
                file.writelines(lines)
        return redirect(url_for('upload_file'))
    except Exception as e:
        print(str(e))
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
