from flask import Flask, render_template, request, session, send_file, make_response, jsonify
import sqlite3
import bcrypt
import datetime
import base64
from mtcnn import FaceModel
import cv2
from io import BytesIO
import numpy as np
# from numplate_model import NumplateModel


app = Flask(__name__)
app.secret_key =  'a468'

face_model = FaceModel()
# plate_model = NumplateModel('./numplate_detection.h5')

@app.route('/')
def index():
    if 'username' in session:
        return render_template('main.html', user=session['username'])
    else:
        return render_template('index.html')
connection = sqlite3.connect('database.db', check_same_thread=False)
if connection:
    print('Connected to the database')
else:
    print('Not connected to the database')

connection.execute('CREATE TABLE IF NOT EXISTS userdata (username TEXT, password TEXT)')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return render_template('main.html', user=session['username'])
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with sqlite3.connect('database.db') as userdata:
            cursor = userdata.cursor()
            cursor.execute('INSERT INTO userdata (username, password) VALUES (?, ?)', (username, encrypted_password))
            userdata.commit()
        return render_template('index.html')
    else:
        return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return render_template('main.html', user=session['username'])

    if request.method == 'POST':
        with sqlite3.connect('database.db') as userdata:
            cursor = userdata.cursor()
            cursor.execute('SELECT * FROM userdata')
            userdata = cursor.fetchall()
            for user in userdata:
                if request.form['username'] == user[0] and bcrypt.checkpw(request.form['password'].encode('utf-8'), user[1]):
                    session['username'] = request.form['username']
                    return render_template('main.html', user=session['username'])
            return 'Invalid username or password'
    else:
        return render_template('login.html')
    
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'username' not in session:
        return render_template('index.html')
    connection.execute('CREATE TABLE IF NOT EXISTS images (timestamp TEXT, username TEXT, filename TEXT, filters TEXT, image BLOB)')

    file = request.files['image']
    filename = request.form['filename']
    filter = ""

    try:
        if file:
            face = request.form.get('face')
            # numplate = request.form.get('numplate')
            image_stream = BytesIO()
            nparr = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if face is not None:
                image = face_model.detect(image)
                filter += "face "
            # if numplate is not None:
            #     image = plate_model.detect(image)
            success, encoded_image = cv2.imencode('.jpg', image)

            # if request.form.get('option') == 'face':
            #     # face wala code
            # else:
            #     # numplate wala code

            if success:
                image_stream.write(encoded_image.tobytes())
                image_stream.seek(0)
                response = make_response(send_file(image_stream, mimetype='image/jpeg'))
                response.headers['Content-Disposition'] = f'attachment; filename={file.filename}'

                encoded_image_base64 = base64.b64encode(encoded_image).decode('utf-8')
                cursor = connection.cursor()
                cursor.execute('INSERT INTO images (timestamp, username, filename, filters, image) VALUES (?, ?, ?, ?, ?)', (str(datetime.datetime.now()), session['username'], filename, filter, encoded_image.tobytes()))
                connection.commit()
                return render_template('main.html', encoded_image=encoded_image_base64, filename=filename)

    except Exception as e:
        return str(e), 500


@app.route('/view')
def view():
    if 'username' not in session:
        return render_template('index.html')
    with sqlite3.connect('database.db') as userdata:
        cursor = userdata.cursor()
        cursor.execute('SELECT timestamp, filename, filters, image FROM images WHERE username = ?', (session['username'],))
        data = cursor.fetchall()
        new_data = []
        for row in data:
            encoded_image = base64.b64encode(row[3]).decode('utf-8')
            new_data.append((row[0], row[1], row[2], encoded_image))
        return render_template('view.html', images=new_data, user=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
