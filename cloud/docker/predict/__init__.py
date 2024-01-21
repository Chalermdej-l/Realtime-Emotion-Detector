import logging
import json
import azure.functions as func
import cv2
import numpy as np
import imutils
import tempfile
from tflite_runtime.interpreter import Interpreter


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:   
        file = req.files['file']            
        type_predict = file.content_type

        logging.info(f'Processing data {type_predict}')

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

        logging.info(f'Returning data with shape {data_shape}...')
        logging.info('---------------------------------------')

        response = {'predict':str(return_data.tobytes()) ,'shape':str(data_shape)}

        return func.HttpResponse(
            body=json.dumps(response),
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
             body=json.dumps({'error': str(e)})             ,
             status_code=400
        )

def load_tflite_model(model_path):
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

def img_toarray(img,type):   
    x = np.asarray(img, dtype="float32")
    if type=='rgb':
        x = x.reshape((x.shape[0], x.shape[1], 3))
    else:
        x = x.reshape((x.shape[0], x.shape[1], 1))

    return np.expand_dims(x, axis=0)

def inference_tflite_model(interpreter, input_data):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_data = input_data.reshape(input_details[0]['shape'])
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

def preprocess_frame(data):
    input_mood = cv2.resize(data, dsize=(48,48))
    input_mood = cv2.cvtColor(input_mood,cv2.COLOR_BGR2GRAY).astype("float") / 255.0

    input_mood = img_toarray(input_mood,'grey')

    return input_mood

def detectface(model_path):
    detector = cv2.CascadeClassifier(model_path)
    return detector


def process_data(data,mood_model,detector,img_size=400):
   
    EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
    AGE = ['0-2', '13-20', '21-32', '33-48', '3-6', '49-53', '54+', '7-12']

    data = imutils.resize(data,img_size)  
    frameClone = data.copy() 
    rects = detector.detectMultiScale(data, 
                                      scaleFactor=1.05, minNeighbors=11, 
                                      minSize=(20, 20),flags=cv2.CASCADE_SCALE_IMAGE)

    if len(rects) > 0:        

        for o,rect in enumerate(rects):                
            (fX, fY, fW, fH) = rect 
            roi = data[fY:fY + fH, fX:fX + fW]
            input_mood = preprocess_frame(roi)            

            preds_mood = inference_tflite_model(mood_model,input_mood)[0]

            label = EMOTIONS[preds_mood.argmax()]

            pos = o+1
            text_all = f'Face {pos} {label} {preds_mood.max()*100:.2f}%'

            if (o % 2) == 0:
                cv2.putText(frameClone, text_all, (fX, fY - (pos*10)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(frameClone, text_all, (fX, fY + fH + (pos*10)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)

    return frameClone


def getdata(type,fp_name):

    img_size=400

    mood_model = './model/keras/mood_model.tflite'
    detector_path = './model/haarcascade/haarcascade_frontalface_default.xml'

    logging.info('Loading model...')
    detector =detectface(detector_path)
    mood_model = load_tflite_model(mood_model)

    logging.info('Making prediction...')
    # Input is an image
    if type =='image/jpeg' :   
        logging.info('Image prediction...') 

        data = cv2.imread(fp_name)
        return_data = process_data(data,mood_model,detector,img_size)
        logging.info('Finish reading data')
    
    # Input is a video
    else:    
        logging.info('Video prediction...') 
        camera = cv2.VideoCapture(fp_name)
        frames = []
        while True:
            grabbed,data = camera.read()
            if not grabbed:
                logging.info('End of Video...')
                break

            pred_data = process_data(data,mood_model,detector,img_size)

            frames.append(pred_data)

        camera.release()
        return_data = np.array(frames)
        logging.info('Finish reading data')

    return return_data