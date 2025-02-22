#way to upload image
#way to save the image
#function to make prediction on the image

import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from flask import Flask,render_template,request
from tensorflow import keras
from keras.optimizers import RMSprop
from keras.preprocessing import image
from keras.preprocessing.image import load_img
from keras.preprocessing.image import ImageDataGenerator
import pickle


app=Flask(__name__,static_folder='./BaseData/static')
upload_path="./BaseData/static"
model=None
def training():
    global model


    train = ImageDataGenerator(rescale=1/201)
    validation=ImageDataGenerator(rescale=1/201)
    #train the model with Face dataset of criminals with different orientations
    # I trained this model with the self collected images of criminals from google
    train_dataset = train.flow_from_directory('./BaseData/Train',
                                         target_size = (200,200),
                                         batch_size = 15,
                                         class_mode = 'binary')
    #keep aside some dataset images for validation purpose.
    validation_dataset = train.flow_from_directory('./BaseData/Validation',
                                         target_size = (200,200),
                                         batch_size = 15,
                                         class_mode = 'binary')                                 
    model = tf.keras.models.Sequential([ tf.keras.layers.Conv2D(16,(3,3),activation = 'relu',input_shape=(200,200,3)),
                                    tf.keras.layers.MaxPool2D(2,2),
                                    #
                                    tf.keras.layers.Conv2D(32,(3,3),activation='relu'),
                                    tf.keras.layers.MaxPool2D(2,2),
                                    #
                                    tf.keras.layers.Conv2D(64,(3,3),activation='relu'),
                                    tf.keras.layers.MaxPool2D(2,2),
                                    #
                                    tf.keras.layers.Flatten(),
                                    #
                                    tf.keras.layers.Dense(512,activation='relu'),
                                    #
                                    tf.keras.layers.Dense(1,activation='sigmoid')
                                   ])
    model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(learning_rate=0.001),
              metrics=['accuracy'])
    model_fit = model.fit(train_dataset,
                     steps_per_epoch=5,
                     epochs=50,
                     validation_data= validation_dataset)
    pickle.dump(model,open('model.sav','wb'))

@app.route("/",methods=["GET","POST"])
def upload_predict():
    image_loc=''
    pred=''
    if(request.method=="POST"):
        image_file=request.files["image"]
        
        if image_file:
            image_loc=os.path.join(
                upload_path,
                image_file.filename
            )
            image_file.save(image_loc)
            img=load_img(upload_path+'/'+image_file.filename,target_size=(200,200))
            x=image.img_to_array(img)
            x=np.expand_dims(x,axis=0)
            images=np.vstack([x])
            model = pickle.load(open('model.sav','rb'))

            if(model):
                val=model.predict(images)
                if val==0:
                    print("Criminal")
                    pred="Criminal"
                else:
                    print("not a Criminal")
                    pred="notCriminal"
        
        return render_template("criminals_index.html",pred=pred,image_loc = image_file.filename)           
    return render_template("criminals_index.html",pred=pred, image_loc = None)
if __name__=="__main__":
    training()
    app.run(debug=True,host="0.0.0.0",port=3000)
