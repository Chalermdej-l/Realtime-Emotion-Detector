import cv2
import numpy as np
import imutils
import os
import glob
import argparse
from tensorflow import lite

def load_tflite_model(model_path):
    interpreter = lite.Interpreter(model_path=model_path)
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

def img_toarray(img,type):   
    x = np.asarray(img, dtype="float32")
    if type=='rgb':
        x = x.reshape((x.shape[0], x.shape[1], 3))
    else:
        x = x.reshape((x.shape[0], x.shape[1], 1))

    return np.expand_dims(x, axis=0)

def preprocess_frame(data):
    input_mood = cv2.resize(data, dsize=(48,48))
    input_mood = cv2.cvtColor(input_mood,cv2.COLOR_BGR2GRAY).astype("float") / 255.0 
    input_mood = img_toarray(input_mood,'grey')
    return input_mood

def detectface(model_path):
    detector = cv2.CascadeClassifier(model_path)
    return detector


def process_data(data,mood_model,detector,img_height=255,img_size=400):

    EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

    data = imutils.resize(data,img_size)
    
    frameClone = data.copy()
    canvas = np.zeros((img_height, img_size, 3), dtype="uint8")
    rects = detector.detectMultiScale(data, 
                                      scaleFactor=1.05, minNeighbors=11, 
                                      minSize=(20, 20),flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) > 0:

        sort_rect = sorted(rects, reverse=False,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))

        for o,rect in enumerate(sort_rect):        

            (fX, fY, fW, fH) = rect 

            roi = data[fY:fY + fH, fX:fX + fW]
            input_mood = preprocess_frame(roi)

            preds_mood = inference_tflite_model(mood_model,input_mood)[0]
    
            label = EMOTIONS[preds_mood.argmax()]

            if o == 0:
                for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds_mood)):
                    # construct the label text
                    text = "{}: {:.2f}%".format(emotion, prob * 100)

                    # draw the label + probability bar on the canvas
                    w = int(prob * img_size)
                    cv2.rectangle(canvas, (5, (i * 35) + 5),
                    (w, (i * 35) + 35), (0, 0, 255), -1)
                    cv2.putText(canvas, text, (10, (i * 35) + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (255, 255, 255), 1, cv2.LINE_AA)

            text_all = f'Face {o+1} {label} {preds_mood.max()*100:.2f}%'
            pos = o+1

            if (o % 2) == 0:
                cv2.putText(frameClone, text_all, (fX, fY - (pos*10)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(frameClone, text_all, (fX, fY + fH + (pos*10)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)


    else:
        label = 'Notfound'
        frameClone = data
    
    return frameClone,canvas,label
    

def getdata(type,mood_model=None,model_age=None,detector_path=None,input_path=None,output_path=None):

    img_size=400
    img_height=255


    mood_model = load_tflite_model(mood_model)    
    detector =detectface(detector_path)

    # Input is an image
    if type =='image' and input_path is not None:
        path_list  = glob.glob(input_path + '/*.jpg')
        if not(path_list):
            print('No image found please look at the path and the image extention is it jpg exit...')
            return
    
        for path in path_list:
            data = cv2.imread(path)

            pred_data,canvas,label = process_data(data,mood_model,detector,img_height,img_size)

            cv2.imshow("Face", pred_data)
            cv2.imshow("Probabilities", canvas)

            cv2.waitKey(0) 
            cv2.destroyAllWindows()

            filename = path.split(os.path.sep)[-1]
            filename = label + '_' + filename
            output_path = output_path+ '//'+ filename
            cv2.imwrite(filename=output_path,img=pred_data)
            
    
    # Input is  video
    else:

        if type =='video' and input_path is not None:
            path_list = glob.glob(input_path +'/*.mp4')
            if not(path_list):
                print('No video found please look at the path and the video extention is it mp4 exit...')
                return
            path = path_list[0]

            filename = path.split(os.path.sep)[-1]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  

            output_path = output_path+ '//'+ f'output_{filename}'
            output_video = cv2.VideoWriter(output_path, fourcc, 30.0, (img_size,225))            

            camera = cv2.VideoCapture(path)

        elif type =='live':
            filename = 'live'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  

            output_path = output_path+ '//'+ f'output_{filename}.mp4'

            output_video = cv2.VideoWriter(output_path, fourcc, 30.0, (img_size,300))

            camera = cv2.VideoCapture(0)

        else:
            print('No path pass if mode is image or video please pass path directory...')
            return 

        while True:
            grabbed,data = camera.read()

            if not grabbed:
                print('End of Video...')
                break

            pred_data,canvas,label = process_data(data,mood_model,detector,img_height,img_size)
            cv2.imshow("Face", pred_data)            
            cv2.imshow("Probabilities Of Face 1", canvas)

            output_video.write(pred_data)
  
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        output_video.release()

        cv2.destroyAllWindows()

        print('Script finish...')


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('-t',  required=True, help='Mode of the data image, video or live.')
    ap.add_argument('-m_m',  required=True, help='Model for mood detection to used.')
    ap.add_argument('-m_a',  required=True, help='Model for age detection to used.')
    ap.add_argument('-d',  required=True, help='Face detector model to used.')
    ap.add_argument('-i', required=True,help='Input of the data directory if mode is live pass None.')
    ap.add_argument('-o',required=True, help='Output of the data directory to save the process data.')

    args = vars(ap.parse_args())   

    getdata(args['t'],args['m_m'],args['m_a'],args['d'],args['i'],args['o']) 
