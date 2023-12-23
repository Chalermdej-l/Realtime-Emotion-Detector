import cv2
import numpy as np
import imutils
import os
import glob
import argparse
from tflite_runtime.interpreter import Interpreter

def load_tflite_model(model_path):
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

def inference_tflite_model(interpreter, input_data):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Assuming the input shape is (batch_size, height, width, channels)
    input_data = input_data.reshape(input_details[0]['shape'])

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

def img_toarray(img):   
    x = np.asarray(img, dtype="float32")
    x = x.reshape((x.shape[0], x.shape[1], 1))

    return x
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
    canvas = np.zeros((img_height, img_size, 3), dtype="uint8")
    rects = detector.detectMultiScale(frame, 
                                      scaleFactor=1.05, minNeighbors=11, 
                                      minSize=(20, 20),flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) > 0:

        sort_rect = sorted(rects, reverse=False,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))

        for o,rect in enumerate(sort_rect):        

            (fX, fY, fW, fH) = rect 

            roi = grey[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float") / 255.0
            roi = img_toarray(roi)
            roi = np.expand_dims(roi, axis=0)
            # preds = model.predict(roi)[0]
            preds = inference_tflite_model(model,roi)[0]
            label = EMOTIONS[preds.argmax()]

            if o == 0:
                for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
                    # construct the label text
                    text = "{}: {:.2f}%".format(emotion, prob * 100)

                    # draw the label + probability bar on the canvas
                    w = int(prob * img_size)
                    cv2.rectangle(canvas, (5, (i * 35) + 5),
                    (w, (i * 35) + 35), (0, 0, 255), -1)
                    cv2.putText(canvas, text, (10, (i * 35) + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (255, 255, 255), 2)
            
            text_all = f'Face {o+1} {label} {preds.max()*100:.2f}%'

            cv2.putText(frameClone, text_all, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)


    else:
        label = 'Notfound'
    
    return frameClone,canvas,label
    

def getdata(type,model_path=None,detector_path=None,input_path=None,output_path=None):

    img_size=400
    img_height=255

    # model = getmodel(model_path)
    model = load_tflite_model(model_path)
    detector =detectface(detector_path)

    # Input is an image
    if type =='image' and input_path is not None:
        path_list  = glob.glob(input_path + '/*.jpg')
        if not(path_list):
            print('No image found please look at the path and the image extention is it jpg exit...')
            return
    
        for path in path_list:
            data = cv2.imread(path)

            pred_data,canvas,label = process_data(data,model,detector,img_height,img_size)

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

            pred_data,canvas,label = process_data(data,model,detector,img_height,img_size)

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
    ap.add_argument('-m',  required=True, help='Model to used.')
    ap.add_argument('-d',  required=True, help='Face detector model to used.')
    ap.add_argument('-i', required=True,help='Input of the data directory if mode is live pass None.')
    ap.add_argument('-o',required=True, help='Output of the data directory to save the process data.')

    args = vars(ap.parse_args())   

    getdata(args['t'],args['m'],args['d'],args['i'],args['o']) 
