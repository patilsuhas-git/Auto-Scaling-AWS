from flask import Flask, render_template, request, redirect, url_for, session
import json
import mysql.connector
import os
# Database credentials.
config = {
    'user': 'USUALLY ROOT',
    'password': 'YOURPASSWORD',
    'host': 'LOCALHOST',
    'database':'DATABASENAME'
}

def connection_db():
    cnx = mysql.connector.connect(
            user = config['user'],
            password = config['password'],
            host = config['host'],
            database = config['database']
        )
    return cnx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/pictures/'
app.secret_key = 'sec key'

@app.route('/', methods=['GET'])
def show_login():
    return render_template('login.html')

@app.route('/gallery', methods=['GET', 'POST'])
def show_gallery() :
    filePath = []
    print('This is session in gallery == ', session)

    cnx_db = connection_db()
    cursor = cnx_db.cursor()

    querySelect = 'select pic.ID, pic.user_id, pic.image_path, pic.image_name, au.name, au.email, au.user_name from pictures pic LEFT JOIN auth_table au on pic.ID = au.ID'
    cursor.execute(querySelect)
    result_set =cursor.fetchall()
    return render_template('home.html', result = result_set, current_user = str(session['current_user_id']), current_user_name = session['user_name'])

@app.route('/commentinsert', methods=['GET','POST'])
def comment_insert() :
    if request.method =='POST':
        comment = request.get_json('data')
        print('This is the value of data ,...,.,.,', comment)
        print('This is session picture id ', session['picture_id'])
        print('This is session user id ', session['current_user_id'])
        cnx_db = connection_db()
        cursor = cnx_db.cursor()
        queryInsert = "Insert into picture_comment (picture_id, user_id, comment) values (%s, %s, %s)"
        cursor.execute(queryInsert, (session['picture_id'], session['current_user_id'], comment, ))
        cnx_db.commit()
    return json.dumps({'success': 'result_set'}, 200, {'contentType': 'application/json'})

@app.route('/commentpic', methods=['GET', 'POST'])
def comment_pic():
    if request.method == 'POST':
        data = request.get_json('data')
        print('This ispost of comment_pic..', data)
        # print('This is it ', data['fromGallery'])
        if data['fromGallery'] == 'true' :
            cnx_db = connection_db()
            cursor = cnx_db.cursor()

            queryComment = "select pc.ID, pc.picture_id, pc.user_id, pc.comment, pic.image_path, pic.ID from picture_comment pc Left Join pictures pic on pc.picture_id = pic.ID where pc.picture_id = %s"
            cursor.execute(queryComment,(int(data['picture_id']), ))

            result_set =cursor.fetchall()

            if(len(result_set) > 0) :
                session['result'] = result_set
                for i in result_set :
                    session['path'] = i[4]
                    session['picture_id'] = i[5]
                return json.dumps({'success': 'result_set'}, 200, {'contentType': 'application/json'})
            else :
                cnx_db1 = connection_db()
                cursor1 = cnx_db1.cursor()

                queryPicture = "Select image_path, ID from pictures where ID = %s"
                cursor1.execute(queryPicture, (int(data['picture_id']), ))
                result_set = cursor1.fetchall()
                session['result'] = 'null'
                session['path'] = result_set[0][0]
                session['picture_id'] = result_set[0][1]
                return json.dumps({'success': 'null'}, 200, {'contentType': 'application/json'})
    elif request.method == 'GET':
        result = session['result']
        cnx_db1 = connection_db()
        cursor1 = cnx_db1.cursor()

        queryComment = "select pc.ID, pc.picture_id, pc.user_id, pc.comment, pic.image_path, pic.ID from picture_comment pc Left Join pictures pic on pc.picture_id = pic.ID where pc.picture_id = %s"
        cursor1.execute(queryComment, (session['picture_id'], ))
        result_set = cursor1.fetchall()
        print ('THis is the result_set in get comment <>><><><<><><', result_set)
        picture_path = session['path'].encode('ascii', 'ignore')
        print ('show picture path')
        return render_template('commentpage.html', result=result_set, picture_path=picture_path)

@app.route('/delete_picture', methods=['GET', 'POST'])
def delete_picture() :
    if request.method == 'POST':
        data = request.get_json('data');
        print('This is delete_picture ========', data)
        data = int(data)
        print('This is delete_picture after conversion========', data)
        cnx_db = connection_db()
        cursor = cnx_db.cursor()

        queryDelete = 'Delete from pictures where ID = %s'
        cursor.execute(queryDelete, (data, ))
        cnx_db.commit()
    return json.dumps({'success': 'Record Deleted'}, 200, {'contentType': 'application/json'})

@app.route('/register_usr', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST' :
        data = request.get_json('data')
        # print data
        datalst = data.split('&')
        name = ''
        email = ''
        username = ''
        password = ''
        for i in datalst:
            if (i.split('=')[0] == 'name') :
                name = i.split('=')[1].strip()
            elif (i.split('=')[0] == 'email') :
                if '%40' in i.split('=')[1] :
                    email = i.split('=')[1].replace('%40', '@')
                else :
                    email = i.split('=')[1]
            elif (i.split('=')[0] == 'username') :
                username = i.split('=')[1]
            elif (i.split('=')[0] == 'password') :
                password = i.split('=')[1]

        cnx_db = connection_db()
        cursor = cnx_db.cursor()
        query = "insert into auth_table(name, email, user_name, passwd) values (%s, %s,  %s, %s)"
        cursor.execute(query, (name, email, username, password, ))
        cnx_db.commit()
        return json.dumps({'success': 'Record Created'}, 200, {'contentType': 'application/json'})
    else :
        return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login() :
    if request.method == 'POST' :
        username = ''
        password = ''
        data = request.get_json('data')
        datalst = data.split('&')
        for i in datalst:
            if (i.split('=')[0] == 'username') :
                username = i.split('=')[1]
            elif (i.split('=')[0] == 'password') :
                password = i.split('=')[1]
        print('This is username : ', username)
        print('This is password : ', password)

        cnx_db = connection_db()
        cursor = cnx_db.cursor()
        query = "Select ID, name, email, user_name, passwd from auth_table where user_name = %s and passwd = %s"
        cursor.execute(query, (username, password, ))
        result_set =cursor.fetchall()
        print('This is the result set ==========>>>>',result_set)
        if len(result_set) == 0 :
            print('There is no data from database')
            return json.dumps({'success': 'Invalid Credential'}, 200, {'contentType': 'application/json'})
        else :
            session['current_user_id'] = result_set[0][0]
            session['name'] = result_set[0][1]
            session['email'] = result_set[0][2]
            session['user_name'] = result_set[0][3]
            print('There is data from database', session['current_user_id'])
            return json.dumps({'success': 'User Authenticated'}, 200, {'contentType': 'application/json'})
            # return redirect(url_for('show_login'))
    elif request.method == 'GET':
        print('This is login get ')
        return render_template('login.html')

@app.route('/uploadImage', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'GET':
        return render_template('uploadpage.html')
    elif request.method == 'POST':
        fileobj = request.files.getlist('file')
        fileobj = fileobj[0]
        filename = fileobj.filename
        filesavepath = os.path.join(app.config['UPLOAD_FOLDER'], filename).encode('ascii', 'ignore')
        print ('This is filepath ==',filesavepath)
        print ('This is filename ==',filename, )
        print ('This is logged in user ==', session['current_user_id'])
        fileobj.save(filesavepath)

        cnx_db = connection_db()
        cursor = cnx_db.cursor()

        queryInsert = 'Insert into pictures(user_id, image_path, image_name) values (%s, %s, %s)'
        cursor.execute(queryInsert, (session['current_user_id'], filesavepath, filename, ))

        cnx_db.commit()
        cursor.close()
        cnx_db.close()
        return redirect(url_for('show_gallery'))

if __name__ == '__main__':
    app.run(debug=True)
