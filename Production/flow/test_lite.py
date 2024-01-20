import cv2
import numpy as np
import imutils
import tempfile
from tflite_runtime.interpreter import Interpreter
from flask import Flask, request, jsonify, send_file, make_response

from waitress import serve



app = Flask('predict_emotion')

def load_tflite_model(model_path):
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

def inference_tflite_model(interpreter, input_data):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_data = input_data.reshape(input_details[0]['shape'])

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

def preprocess_frame(data,img_size):
    data = imutils.resize(data, width=img_size)
    grey = cv2.cvtColor(data,cv2.COLOR_BGR2GRAY)

    return data,grey

def detectface(model_path):
    detector = cv2.CascadeClassifier(model_path)
    return detector

def img_toarray(img):   
    x = np.asarray(img, dtype="float32")

    x = x.reshape((x.shape[0], x.shape[1], 1))

    return x


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
            roi = np.expand_dims(roi, axis=0)
            preds = inference_tflite_model(model,roi)[0]
            label = EMOTIONS[preds.argmax()]
           
            
            text_all = f'Face {o+1} {label} {preds.max()*100:.2f}%'

            cv2.putText(frameClone, text_all, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)

    return frameClone


def getdata(type,fp_name):

    img_size=400
    img_height=255

    print('Loading model...')

    model = model = load_tflite_model('../model/keras/best_model.tflite')
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
            fp = tempfile.NamedTemporaryFile(suffix='.jpg',delete=False)
            fp.write(file.read())      
            fp.close()   
        else:
            fp = tempfile.NamedTemporaryFile(suffix='.mp4',delete=False)
            fp.write(file.read())  
            fp.close()           

        return_data = getdata(type_predict,fp.name)
        data_shape = return_data.shape

        print(f'Returning data with shape {data_shape}...')
        print('---------------------------------------')

        response = {'predict':str(return_data.tobytes())
                    ,'shape':str(data_shape)}
        return jsonify(response)
    

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    serve(app=app,host='0.0.0.0',port=9696)
