from flask import Flask, render_template, request, session
import sqlite3
import bcrypt
import datetime

app = Flask(__name__)
app.secret_key =  'a468'


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
    if request.method == 'POST':
        connection.execute('CREATE TABLE IF NOT EXISTS images (timestamp TEXT, username TEXT, image BLOB)')
        image = request.files['image']
        with sqlite3.connect('database.db') as userdata:
            cursor = userdata.cursor()
            cursor.execute('INSERT INTO images (timestamp, username, image) VALUES (?, ?, ?)', (str(datetime.datetime.now()), session['username'], image.read()))
            userdata.commit()
        return '<script>alert("Upload Successful!")</script>'
    else:
        return render_template('upload.html') 


@app.route('/view')
def view():
    if 'username' not in session:
        return render_template('index.html')
    with sqlite3.connect('database.db') as userdata:
        cursor = userdata.cursor()
        cursor.execute('SELECT * FROM images WHERE username = ?', (session['username'],))
        images = cursor.fetchall()
        return render_template('view.html', images=images)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)