import requests
import cv2
import numpy as np
import argparse 

import glob
import os

def main(inpath,outpath,mode,url):
    
    if mode == 'img':
        inpath = os.path.sep.join([inpath,'/*.jpg'])
        test_img_list = glob.glob(inpath + '',recursive=True)

        for img in test_img_list:
            print(img)
            with open(img, "rb") as test_file:
                files = {'file':  ('test1.jpg', test_file.read(), 'image/jpeg')}  
            print('Sending file to API ...')      
            response = requests.post(url, files=files)
            print(response.status_code)
            filename=  os.path.split(img)[-1]
            response_json = response.json()
            shape = eval(response_json['shape'])
            response_reshape= np.frombuffer(eval(response_json['predict']), np.uint8).reshape(shape)
            new_path = os.path.sep.join([outpath,filename])
            cv2.imwrite(new_path,response_reshape)
            
    
    else:
        inpath = os.path.sep.join([inpath,'/*.mp4'])
        test_vid_list = glob.glob(inpath,recursive=True)

        for vid in test_vid_list:
            print(vid)
            with open(vid, "rb") as test_file:
                files = {'file':  ('testvideo.mp4', test_file.read(), 'video/mp4')}  


            print('Sending file to API ...')            
            response = requests.post(url, files=files)
            print(response.status_code)
            response_json = response.json()
            shape = eval(response_json['shape'])
            response_reshape= np.frombuffer(eval(response_json['predict']), np.uint8).reshape(shape)

            filename=  os.path.split(vid)[-1]
            new_path = os.path.sep.join([outpath,filename])

            fourcc = cv2.VideoWriter_fourcc(*'MP4V')  
            output_video = cv2.VideoWriter(new_path, fourcc, 30.0, (shape[2:0:-1]))    
            for i in response_reshape:
                output_video.write(i)       
            output_video.release()
    print('Script Finish Processing file.')

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('-i',  required=True, help='Input path.')
    ap.add_argument('-o',  required=True, help='Output path.')
    ap.add_argument('-m',  required=True, help='Mode of the file img or vid.')   
    ap.add_argument('-u',  required=True, help='Url of the function.')   


    args = vars(ap.parse_args())   

    main(args['i'],args['o'],args['m'],args['u']) 
