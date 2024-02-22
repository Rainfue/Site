# Load operation system library
import os

# Website libraries
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import date




# Load math library
import numpy as np

# Load nessecery libraries
import re
from yandex_music import Client
from random import randint
from time import asctime as date

# Load machine learning libraries
from keras.preprocessing import image
from keras.models import load_model

# Where I will keep user uploads
UPLOAD_FOLDER = 'static\\uploads'
# Allowed files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Machine Learning Model Filename
ML_MODEL_FILENAME = r'D:\PhotoMusic Project\Site\model\album_image_model.h5'

classes = ['alternative', 'classical', 'electronics', 'metal', 'pop', 'rap', 'rock'] 

# Create the website object
app = Flask(__name__)

#Try to allow only images
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Define the view for the top level page
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    #Initial webpage load
    if request.method == 'GET' :
        return render_template('index.html')
    else: # if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser may also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # If it doesn't look like an image file
        if not allowed_file(file.filename):
            flash('I only accept files of type'+str(ALLOWED_EXTENSIONS))
            return redirect(request.url)
        #When the user uploads a file with good parameters
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    test_image = image.load_img(UPLOAD_FOLDER+"/"+filename, target_size=(128,128))
    # Convert the image to an array
    test_image = image.img_to_array(test_image)
    # Changing the shape of the array into a flat vector
    test_image = test_image.reshape(1, 128, 128, 3)
    # Invertize the image
    test_image = 255 - test_image
    # Normalize the image
    test_image /= 255
    
    def give_index(request, num):
        client = Client('y0_AgAAAABUzxkNAAG8XgAAAAD5FT2pAAANjfSxyG5KUJGWZL4YyRTcLHW4qQ').init()
        try:
            search = client.search(f'{request}',
                            nocorrect=False, 
                            page=randint(1, 99), 
                            type_ = 'album')
        except IndexError:
            search = client.search(f'{request}',
                            nocorrect=False, 
                            page=1, 
                            type_ = 'album')

        search_split = str(search).split('}, {')
        album_name_list = []

        for el in search_split:
            string = str(el)

            # Извлечение названия
            
            start_index = string.find("'genre': ") + len("'genre': ")
            end_index = string.find(",", start_index)
            
            start_index2 = string.find("'id': '") + len("'id': '")
            end_index2 = string.find(",", start_index2)
            name2 = string[start_index2:end_index2]
            album_name_list.append(name2)
            
        return (album_name_list[2:len(album_name_list)])[0:num]

    def give_track_id(id, num):
    
        token='y0_AgAAAABUzxkNAAG8XgAAAAD5FT2pAAANjfSxyG5KUJGWZL4YyRTcLHW4qQ'
        client=Client(token=token).init()
        try:
            album_info = ((str(client.albumsWithTracks(id)).split("[[{"))[1])
        except IndexError:
            album_info = ((str(client.albumsWithTracks(id)).split("[[{"))[0])
            id_tracks = ['28973341']
            return id_tracks
                
        pattern = r"'id': '\d+"
        id_tracks2 = re.findall(pattern, album_info)
        id_tracks = []
        id_tracks3 = []
        for el in id_tracks2:
            result = re.findall(r'\d+', el)
            id_tracks3.append(result)
            for x in id_tracks3:
                id_tracks.extend(x if isinstance(x, list) else [x])
        return list(set(id_tracks))[0:num]
    
    def create_playlist(predict1, predict2, predict3):
        from datetime import date
    
        token='y0_AgAAAABUzxkNAAG8XgAAAAD5FT2pAAANjfSxyG5KUJGWZL4YyRTcLHW4qQ'
        client=Client(token=token).init()
        old=[]
        new=""
        # name = date.today().strftime("%d/%m/%")
        for elem in Client.users_playlists_list(self=client):
            old.append(elem["kind"])
        Client.users_playlists_create(self=client,title=f"PhotoMusic {predict1} {date.today().strftime('%d/%m/%y')}")
        for elem in Client.users_playlists_list(self=client):
            if elem["kind"] not in old:
                new=elem["kind"]

        predict_list = [predict1, predict2, predict3]        

        j=0

        for i in range(len(predict_list)):
            match i:
                case 0:
                    id_album_list = give_index(predict_list[i], 5)
                case 1:
                    id_album_list = give_index(predict_list[i], 3)
                case 2:
                    id_album_list = give_index(predict_list[i], 2)

            
            for el in id_album_list:
                album_id = el
                track_list = give_track_id(el, 3)
                for i in range(1,len(track_list)+1):    
                    Client.users_playlists_insert_track(self=client,
                                                        kind=new,
                                                        album_id=f"{album_id}", 
                                                        revision=i+j,
                                                        track_id=f"{track_list[i-1]}")
                j+=len(track_list)
        
        return f"https://music.yandex.ru/users/mrrainfue/playlists/{new}"
    
    model = load_model(ML_MODEL_FILENAME)
    prediction = model.predict(test_image)
    sorted_array = np.argsort(prediction[0], axis=0)
    prediction1 = np.argmax(prediction) 
    prediction2 = sorted_array[5]
    prediction3 = sorted_array[4]
    
    playlist_link = create_playlist(classes[prediction1], {classes[prediction2]}, {classes[prediction3]})
    
    image_src = "/"+UPLOAD_FOLDER +"/"+filename
    
    results = "<div class='col text-center'><img width='300' height='300' src='"+image_src+"' class='img-thumbnail' /></div><div class='col'></div><div class='w-100'></div>"
    link = playlist_link


    
    return render_template('index.html', len=len(results), results=results, link=link)

@app.route("/about")
def about():
    return render_template('about.html')

def main():
    model = load_model(ML_MODEL_FILENAME)

    app.config['MODEL'] = model
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16MB upload limit
    app.run(debug=True)

# Create a running list of results
results = []

#Launch everything
main()
