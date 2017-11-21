# coding=utf-8
import os
from flask import Flask,url_for,request,render_template,redirect,escape,flash
from werkzeug import secure_filename
import base64, string, random
import shutil, subprocess, multiprocessing
import hashlib
import time

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS_VID = set(['avi'])
ALLOWED_EXTENSIONS_PIC = set(['jpg', 'jpge', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024


@app.route('/' , methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/train-pic' , methods = ['GET', 'POST'])
def trainPic():
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            #照片上傳模式
            print('Get name file: '+ name)
            peoplefile = 'training-images/'+ name
            newfile(peoplefile)
            try:
                filelist = request.files.getlist("file")
                for file in filelist:
                    if file and allowed_file(file.filename.lower() , 'picture'): 
                        file.save(os.path.join(peoplefile, id_generator()+'.jpg') )
                    else:
                        return alertmsg('Error: 檔案格式不符')
                return alertmsg('上傳成功!')
            except:
                return alertmsg('Error: 上傳失敗')
        else:
            return ('Error: 請輸入名字')
    else:
        return render_template('train-pic.html')

   
@app.route('/train-cam' , methods = ['GET', 'POST'])
def trainCam():
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            #拍照上傳模式
            picbase64 = request.form['pic']
            if hashlib.md5(picbase64.encode(encoding='UTF-8') ).hexdigest() != '75acd48bad3bbd6f4f5f9b90a4e91cf4':
                print('Get a name: '+ name)
                picbase64 = picbase64[22:].encode()
                peoplefile = 'training-images/'+ name
                newfile(peoplefile)
                    
                with open(peoplefile+'/'+id_generator()+".png", "wb") as fh:
                    fh.write(base64.decodebytes(picbase64))
                return ('上傳成功!')
            else:
                return ('Error: 沒有照相機')
        else:
            return ('Error: 請輸入名字')
    else:
        return render_template('train-cam.html')

        
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file'] 
        vodname = request.form['vod_date'] +'_'+ request.form['vod_time'].replace(':', '')
        file.filename = file.filename.lower()
        if file and allowed_file(file.filename , 'video'): 
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
        videoname = secure_filename(videoname)
        #建立進程池
        if os.path.isfile('ing') != True:
            open('ing', 'w').close()
            open('videoname', 'w').write(videoname)
            multiprocessing.freeze_support() #避免RuntimeError(win)
            pool = multiprocessing.Pool()
            pool.apply_async(videotask, args=(videoname,))
            #pool.close()
            #pool.join()
            return redirect(url_for('result'))
        else:
            return alertmsg('Error: 前次的辨識尚未完成')
    else:
        #產生影片檔及姓名選單
        videolist = os.listdir(app.config['UPLOAD_FOLDER'])
        for video in videolist:
            flash(video, 'videos')
        namelist = os.listdir('training-images')
        for name in namelist:
            flash(name, 'names')
        return render_template('analysis.html')


@app.route('/result' , methods = ['GET'])
def result():
    if os.path.isfile('ing'):
        return render_template('wait.html')
    elif os.path.isfile('result.txt'):
        flash(getvideoname(), 'video')
        timetable()
        flash(time.time(), 'timejs')
        namelist = os.listdir('training-images')
        for name in namelist:
            flash(name, 'names')
    else:
        flash('沒有任何結果', 'err')
    return render_template('result.html')

    
@app.route('/result/<username>' , methods = ['GET'])
def user_result(username):
    namelist = os.listdir('training-images')
    if username in namelist:
        flash(username, 'names')       
        totalsec = 0
        file = open('result.txt')
        line = file.readline()
        while line:
            sec = line.split("'")
            peoplename = sec[1]           
            if(username == peoplename):
                sec = sec[-1][1:].strip()
                flash(getvideoname()+'/'+sec, 'image')
                totalsec = totalsec + 1
            line = file.readline()
        file.close()
        flash(totalsec, 'detail')
        return render_template('user-result.html') 
    else:
        return render_template('404.html') 
    

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
        namelist = os.listdir('training-images')
        #縮圖建立
        for name in namelist:
            name = name.strip()
            try:
                files= os.listdir('training-images/'+ name )
                shutil.copy2('training-images/'+ name +'/'+files[0], 'static/'+ name +'.png')
            except:
                return render_template('500.html'), 500
        #產生影片及姓名選取方塊
        videolist = os.listdir(app.config['UPLOAD_FOLDER'])
        for vide in videolist:
            flash(vide, 'videos')
        for name in namelist:
            flash(name, 'names')
            piclist = os.listdir('training-images/'+ name)
            flash(name + ' ( '+ str(len(piclist)) +'張照片)', 'people')         
        return render_template('admin.html')
    

@app.route('/admin/<username>' , methods = ['GET'])
def admin_file(username):
    namelist = os.listdir('training-images')
    if username in namelist:
        flash(username, 'names')
        piclist = os.listdir('training-images/'+ username)
        for pic in piclist:
            f = open('training-images/'+ username + '/' + pic,'rb')
            picbase64 = base64.b64encode(f.read())
            f.close()
            picbase64 = (str(picbase64))[2:-1]
            flash(picbase64, 'image')
        return render_template('admin-file.html') 
    else:
        return render_template('404.html') 

    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def bad_request(e):
    return render_template('500.html'), 500

def allowed_file(filename , filetype): 
    if filetype == 'picture':
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_PIC
    else:
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_VID

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
    
def facechange():
    if os.path.exists('facelist.txt'):
        f = open('facelist.txt', 'r')
        facelisttxt = f.read()
        f.close()
        facelist = ''
        for i in os.walk('training-images'):
            facelist = facelist + str(i)
        #比較是否更動
        if facelisttxt == facelist:
            return False
        else:
            f = open('facelist.txt', 'w')
            for i in os.walk('training-images'):
                f.write(str(i))
            f.close()
            return True
    else:
        #不存在則建立
        f = open('facelist.txt', 'w')
        for i in os.walk('training-images'):
            f.write(str(i))
        f.close()
        return True

def videotask(videoname):
    try:
        subprocess.call(['rm', 'result.txt'])
        if facechange():
            subprocess.call(['sh', 'start.sh'])
        subprocess.call(['python', 'video.py', 'generated-embeddings/classifier.pkl','uploads/' + videoname])
    except:
        pass
    finally:
        removefile('ing')
    return 0
   
def timetable():
    f = open('static/assets/time.js', 'w', encoding = 'utf-8')
    f.write('''var chart = AmCharts.makeChart( "chartdiv", {
    "type": "gantt",
    "theme": "light",
    "marginRight": 70,
    "period": "ss",
    "dataDateFormat":"YYYY-MM-DD",
    "balloonDateFormat": "JJ:NN:SS",
    "columnWidth": 0.5,
    "valueAxis": {
        "type": "date"
    },
    "brightnessStep": 10,
    "graph": {
        "fillAlphas": 1,
        "balloonText": "<b>[[task]]</b>: [[open]] [[value]]"
    },
    "rotate": true,
    "categoryField": "category",
    "segmentsField": "segments",
    "colorField": "color",
    "startDate": "''')
    f.write('2017-10-01')
    f.write('''",
    "startField": "start",
    "endField": "end",
    "durationField": "duration",
    "dataProvider": [ ''')
    #圖表內容
    namelist = os.listdir('training-images')
    for name in namelist:
        f.write('''{
        "category": "'''+ name +'''",
        "segments": [ ''')
        
        if os.path.isfile('result.txt'):
            file = open('result.txt')
            line = file.readline()
            while line:
                sec = line.split("'")
                peoplename = sec[1]           
                if(name == peoplename):
                    sec = sec[-1][1:]
                    f.write('''{
                        "start": '''+ sec +''',
                        "duration": 1,
                        "color": "#33CCFF"
                    },''')
                
                line = file.readline()
            file.close()
        f.write(''']
        },''')
    
    f.write(''' ],
        "valueScrollbar": {
            "autoGridCount":false
        },
        "chartCursor": {
            "cursorColor":"#55bb76",
            "valueBalloonsEnabled": false,
            "cursorAlpha": 0,
            "valueLineAlpha":0.5,
            "valueLineBalloonEnabled": true,
            "valueLineEnabled": true,
            "zoomable":false,
            "valueZoomable":true
        },
        "export": {
            "enabled": true
         }
    } );''')
    f.close()

def getvideoname():
    try:
        videoname = open('videoname', 'r').read()
        videoname = videoname.split('.')[0]
        return videoname
    except:
        return 'null'

    
    
if __name__ == '__main__':
    app.debug = True
    app.secret_key = '6Le7Lx0UAA996OzccZzh6IKgBN9B4d5XCuK1uQXwJ' 
    newfile('uploads')
    newfile('training-images')
    removefile('ing')
    app.run(host = '0.0.0.0')
    