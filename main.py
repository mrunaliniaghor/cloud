
import pymongo
# import gridfs
from flask import Flask, render_template, request, session
from pymongo import MongoClient
import uuid
import base64
import datetime
import os

app = Flask(__name__)
app.secret_key = "Mrunalini"


def a():
    return "Inside a"

@app.route('/')
def index():
    # return 'Hello'
    if session.get('logged_in') == True:
        return render_template('upload.html')
    else:
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    client = MongoClient('mongodb://8.34.212.147:27017/')
    u = request.form['user'];
    p = request.form['pass'];
    users = client.mrudb.login.find_one({"username": u})
    pass1 = users['pwd']

    if str(pass1) == str(p):
        session['logged_in'] = True
        return render_template('upload.html')
    else:
        session['logged_in'] = False
        client.close()
        return render_template('login.html')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'jpe'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def insert_img(username, post_id, image_data, filename, cmnt, size_in_kb):
    client = MongoClient('mongodb://8.34.212.147:27017/')
    img_coll = client.mrudb.images
    post_dict = {}
    post_dict['filename'] = filename
    post_dict['username'] = username
    post_dict['post_id'] = post_id
    encoded_string = base64.b64encode(image_data)
    post_dict['image_data'] = encoded_string
    post_dict['post_time'] = str(datetime.datetime.now())
    post_dict['comments'] = str(cmnt)
    post_dict['size'] = str(size_in_kb)
    output = img_coll.save(post_dict)
    images1 = client.mrudb.comments.insert({"username": "mru", "filename": filename, "comment": cmnt})
    client.close()
    return str(output) + "" + str(cmnt)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    client = MongoClient('mongodb://8.34.212.147:27017/')
    cmnt = []
    print 'in upload'
    file = request.files['myfile']
    size1 = os.stat(file.filename).st_size
    size_in_kb = size1 / 1024;
    allowed_size = 1000;
    allowed_count = 20;
    allowed_total_size = 10000
    cmnt = request.form['comments']
    username = "mru"
    total_size = 0

    count1 = client.mrudb.images.find({"username": "mru"}).count()
    total1 = client.mrudb.images.find({"username": "mru"})
    for total2 in total1:
        total_size = total_size + int(total2['size'])

    if file and allowed_file(file.filename):
        if size_in_kb < allowed_size and count1 < allowed_count and (allowed_total_size - total_size) > size_in_kb:
            fname = str(file.filename)
            image_data = open(fname, "rb").read()
            post_id = str(uuid.uuid1())
            output = insert_img(username, post_id, image_data, str(file.filename), cmnt, size_in_kb)
        else:
            client.close()
            return "file size exceeded or count exceeded or less limit"
    client.close()
    return str(allowed_total_size - total_size)


@app.route('/show', methods=['GET', 'POST'])
def show():
    client = MongoClient('mongodb://8.34.212.147:27017/')
    l = ""
    a = []
    b = []
    images1 = client.mrudb.images.find({"username": "mru"})
    for images2 in images1:
        imagename = images2['filename']
        imagecontent = images2['image_data']

        print "imagesname: " + str(imagename)
        a.append(imagecontent)
        b.append(imagename)
    client.close()
    return render_template('display.html', result=a, name1=b)


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    client = MongoClient('mongodb://8.34.212.147:27017/')
    print "in comments"
    cc1 = request.form['comment1']
    cc2 = request.form['filename1']
    images1 = client.mrudb.comments.insert({"username": "mru", "filename": cc2, "comment": cc1})
    client.close()
    return "success comments"


@app.route('/del1/<fol>', methods=['GET', 'POST'])
def del1(fol):
    client = MongoClient('mongodb://8.34.212.147:27017/')
    print "in del"
    # cc1=request.form['comment1']
    images1 = client.mrudb.images.remove({"username": "mru", "filename": fol})
    client.close()
    return "Deleted successfully"


@app.route('/delete/<folder_name>', methods=['GET', 'POST'])
def delete(folder_name):
    client = MongoClient('mongodb://8.34.212.147:27017/')
    images1 = client.mrudb.images.find({"filename": folder_name})
    imgs = []
    com1 = []
    for images2 in images1:
        imgs.append(images2)
        # imagename=images2['filename']
        # print "imagesname: "+str(imagename)
    for i1 in imgs:
        img1 = i1['image_data']
        comments = i1['comments']
        decode = img1.decode()
    images1 = client.mrudb.comments.find({"filename": folder_name, "username": "mru"})
    for images2 in images1:
        com1.append(images2['comment'])
    client.close()
    return render_template('comment.html', result=decode, comm=com1, file=folder_name)


@app.route('/display', methods=['GET', 'POST'])
def display():
    client = MongoClient('mongodb://8.34.212.147:27017/')
    images1 = client.mrudb.images.find()
    imgs = []
    for images2 in images1:
        imgs.append(images2)

    for i1 in imgs:
        img1 = i1['image_data']
        comments = i1['comments']
        decode = img1.decode()
    client.close()
    return render_template('result.html', result=decode)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('login.html')


if __name__ == "__main__":
    app.run()


