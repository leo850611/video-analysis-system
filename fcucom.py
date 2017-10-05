# coding=utf-8
import os
from flask import Flask,url_for,request,render_template,redirect,escape,flash
from werkzeug import secure_filename
import base64
import sqlite3

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['mp4', 'avi', 'mkv', 'wmv', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
#"{{ url_for('static', filename='')}}"

@app.route('/' , methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

    
@app.route('/train' , methods = ['GET', 'POST'])
def train():
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            print('Get a name: '+ name)
            picbase64 = request.form['pic']
            picbase64 = picbase64[22:].encode()
            with open("imageToSave.png", "wb") as fh:
                fh.write(base64.decodebytes(picbase64))
            ##todo
            
            flash('上傳成功!')
            return redirect(url_for('train'))
        else:
            print('NoName')
            flash('請輸入名字')
            return redirect(url_for('train'))
    else:
        return render_template('train.html')
    
    
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file.filename = file.filename.lower()

        if file and allowed_file(file.filename): 
            filename = secure_filename(file.filename) 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
            #return redirect( url_for( 'uploads', filename = filename )) 
            return alertmsg('上傳成功!')
        else:
            return alertmsg('檔案格式不符')
    else:
        return render_template('upload.html')
    
    
@app.route('/analysis' , methods = ['GET'])
def analysis():
    return render_template('analysis.html')

    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def alertmsg(msg):
    return '''
    <script>
        alert(' ''' + msg + ''' ');
        window.history.go(-1);
    </script>'''


if __name__ == '__main__':
    app.debug = True
    app.secret_key = '6Le7Lx0UAA996OzccZzh6IKgBN9B4d5XCuK1uQXwJ' 
    app.run(host = '0.0.0.0')
    