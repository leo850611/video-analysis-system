# coding=utf-8
import os
from flask import Flask,url_for,request,render_template,redirect,escape,flash
from werkzeug import secure_filename
import base64, string, random
import shutil, subprocess, multiprocessing


UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['mp4', 'avi', 'mkv', 'wmv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024


@app.route('/' , methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/train' , methods = ['GET', 'POST'])
def train():
    if request.method == 'POST':
        name = request.form['name']
        picbase64 = request.form['pic']
        
        if name != '':
            if picbase64[:209] != 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgCAYAAAA10dzkAAAYlklEQVR4Xu3WQQEAAAgCMelf2iA3GzB8sHMECBAgQIAAAQIpgaXSCkuAAAECBAgQIHAGoCcgQIAAAQIECMQEDMBY4eISIECAAAECBAxAP0CAAAECBAgQiAkYgLHCxSVAgAABAgQIGIB':
                print('Get a name: '+ name)
                picbase64 = picbase64[22:].encode()
                peoplefile = 'training-images/'+ name
                newfile(peoplefile) #依人名產生資料夾
                
                with open(peoplefile+'/'+id_generator()+".png", "wb") as fh:
                    fh.write(base64.decodebytes(picbase64))
                flash('上傳成功!')
                return redirect(url_for('train'))
            else:
                flash('Error: 沒有照相機')
                return redirect(url_for('train'))
        else:
            flash('請輸入名字')
            return redirect(url_for('train'))
    else:
        return render_template('train.html')
    
    
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file'] 
        vodname = request.form['vod_date'] +'_'+ request.form['vod_time'].replace(':', '')
        file.filename = file.filename.lower()
        if file and allowed_file(file.filename): 
            filename = secure_filename(file.filename)
            filename = vodname + os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
            return alertmsg('上傳成功!')
        else:
            return alertmsg('Error: 檔案格式不符')
    else:
        return render_template('upload.html')
    
    
@app.route('/analysis' , methods = ['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        videoname = request.form['videoname']
        peoplename = request.form['peoplename']
        videoname = secure_filename(videoname)
        peoplename = secure_filename(peoplename)
        #建立進程池
        if os.path.isfile('ing') != True:
            open('ing', 'w').close()
            multiprocessing.freeze_support() #避免RuntimeError(win)
            pool = multiprocessing.Pool()
            pool.apply_async(videotask, args=(videoname,peoplename,))
            #pool.close()
            #pool.join()
            return alertmsg('請等待比對結果!')
        else:
            return alertmsg('Error: 前次的辨識尚未完成')
    else:
        #產生影片檔及姓名選單
        videolist = os.listdir(app.config['UPLOAD_FOLDER'])
        for i in videolist:
            flash(i, 'videos')
        namelist = os.listdir('training-images')
        for i in namelist:
            flash(i, 'names')
        return render_template('analysis.html')


@app.route('/result' , methods = ['GET'])
def result():
    if os.path.isfile('ing'):
        flash('正在進行辨識......', 'err')
    elif os.path.isfile('result.txt'):
        file = open('result.txt')
        line = file.readline()
        while line:
            min = 0
            sec = line.split("'")
            peoplename = sec[1]           
            sec = int(sec[2][1:])
            while sec >= 60:
                sec = sec - 60
                min = min + 1
            if peoplename != 'unknown':
                flash(peoplename +' - '+ str(min) +'分'+ str(sec) +'秒', 'who')
            line = file.readline()
        file.close()
    else:
        flash('沒有任何結果', 'err')
    return render_template('result.html')


@app.route('/admin' , methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        videolist = request.form.getlist('delvideo')
        namelist = request.form.getlist('delname')
        try:
            for i in videolist:
                filename = secure_filename(i)
                os.remove(app.config['UPLOAD_FOLDER']+'/'+ filename)
                print('del video: ' + filename)
            for i in namelist:
                filename = secure_filename(i)
                shutil.rmtree('training-images/'+ filename)
                print('del name: ' + filename)
            return alertmsg('刪除成功!')
        except:
            return alertmsg('Error: 刪除失敗')
    else:
        #產生影片及姓名選取方塊
        videolist = os.listdir(app.config['UPLOAD_FOLDER'])
        for i in videolist:
            flash(i, 'videos')
        namelist = os.listdir('training-images')
        for i in namelist:
            flash(i, 'names')
            piclist = os.listdir('training-images/'+ i)
            flash(i + ' ( '+ str(len(piclist)) +'張照片)', 'people')         
        return render_template('admin.html')
    
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def bad_request(e):
    return render_template('500.html'), 500

def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def alertmsg(msg):
    return '''
    <script>
        alert(' ''' + msg + ''' ');
        window.history.go(-1);
    </script>'''

def newfile(filename):
    if not os.path.exists(filename):
        os.mkdir(filename)

def id_generator(chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(6))

def removefile(filename):
    try:
        os.remove(filename)
    except:
        pass
    
def videotask(videoname, peoplename):
    subprocess.call(['sh', 'start.sh'])
    subprocess.call(['python', 'video.py', 'generated-embeddings/classifier.pkl','uploads/' + videoname])
    removefile('ing')
    return 0
   
   
if __name__ == '__main__':
    app.debug = True
    app.secret_key = '6Le7Lx0UAA996OzccZzh6IKgBN9B4d5XCuK1uQXwJ' 
    newfile('uploads')
    newfile('training-images')
    removefile('ing')
    
    app.run(host = '0.0.0.0')
    