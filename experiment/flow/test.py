import cv2
import numpy as np
import imutils
import io
import tempfile
import os 

from flask import Flask, request, jsonify, send_file, make_response

from waitress import serve
from keras.preprocessing.image import img_to_array
from tensorflow import keras

app = Flask('predict_emotion')

def getmodel(model_path):
    model =keras.models.load_model(model_path)
    return model

def preprocess_frame(data,img_size):
    data = imutils.resize(data, width=img_size)
    grey = cv2.cvtColor(data,cv2.COLOR_BGR2GRAY)

    return data,grey

def detectface(model_path):
    detector = cv2.CascadeClassifier(model_path)
    return detector


def process_data(data,model,detector,img_height=255,img_size=400):

    EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

    frame,grey = preprocess_frame(data,img_size)    
    frameClone = frame.copy()
    rects = detector.detectMultiScale(frame, 
                                      scaleFactor=1.05, minNeighbors=11, 
                                      minSize=(20, 20),flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) > 0:
        for o,rect in enumerate(rects):        

            (fX, fY, fW, fH) = rect 
            roi = grey[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            preds = model.predict(roi)[0]
            label = EMOTIONS[preds.argmax()]
           
            
            text_all = f'Face {o+1} {label} {preds.max()*100:.2f}%'

            cv2.putText(frameClone, text_all, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)

    return frameClone


def getdata(type,fp_name):

    img_size=400
    img_height=255

    print('Loading model...')

    model = getmodel('../model/keras/best_model.hdf5')
    detector =detectface('../model/haarcascade/haarcascade_frontalface_default.xml')

    print('Making prediction...')
    # Input is an image
    if type =='image/jpeg' :   
        print('Image prediction...') 

        data = cv2.imread(fp_name)
        return_data = process_data(data,model,detector,img_height,img_size)
    
    # Input is a video
    else:    
        print('Video prediction...') 
        camera = cv2.VideoCapture(fp_name)
        frames = []
        while True:
            grabbed,data = camera.read()
            if not grabbed:
                print('End of Video...')
                break

            pred_data = process_data(data,model,detector,img_height,img_size)

            frames.append(pred_data)

        camera.release()
        return_data = np.array(frames)

    return return_data

@app.route('/predict', methods=['POST'])
def predict_video():

    print('Received request...')

    try:   
        file = request.files['file']            
        type_predict = file.content_type

        print(f'Processing data {type_predict}')

        if type_predict == 'image/jpeg':
            mimetype = 'image/jpeg'
            fp = tempfile.NamedTemporaryFile(suffix='.jpg',delete=False)
            fp.write(file.read())      
            fp.close()   
        else:
            mimetype = 'video/mp4'
            fp = tempfile.NamedTemporaryFile(suffix='.mp4',delete=False)
            fp.write(file.read())  
            fp.close()           

        return_data = getdata(type_predict,fp.name)
        data_shape = return_data.shape

        print(f'Returning data with shape {data_shape}...')
        print('---------------------------------------')

        # response = make_response(return_data.tobytes())

        # return send_file(io.BytesIO(response), mimetype=mimetype, as_attachment=True,download_name=file.name)

        response = {'predict':str(return_data.tobytes())
                    ,'shape':str(data_shape)}
        return jsonify(response)
    

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    serve(app=app,host='0.0.0.0',port=9696)
