from flask import Flask, render_template, Response,request
import cv2
import pyzbar.pyzbar as pyzbar
import time

import pymongo
from pymongo import MongoClient 

cluster = MongoClient("mongodb+srv://root:toor@cluster0.varlalw.mongodb.net/?retryWrites=true&w=majorityy")
db = cluster["gg"]
collection = db["123"]

app = Flask(__name__)

# initialize the camera capture object
cap = cv2.VideoCapture(0)

# define a generator function that yields frames from the camera
def gen_frames():
    while True:
        # read a frame from the camera
        ret, frame = cap.read()

        # decode any barcodes in the frame
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the barcode data and type
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            # print("[INFO] Found {} barcode: {}".format(barcode_type, barcode_data))
            collection.insert_one({"_id":barcode_data})
            #with open("barcode_result.txt", mode ='w') as file:
            #  file.write("Recognized Barcode:" + barcode_data)
            # cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
        
            # font = cv2.FONT_HERSHEY_DUPLEX
            # cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

            cap.release()
            cv2.destroyAllWindows()
            
            # yield the barcode data as a server-sent event
            yield f"data: {barcode_data}\n\n"
            time.sleep(0.1)  # add a small delay to avoid flooding the browser with events

        # encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)

        # yield the frame as bytes in a response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':


        if request.method == 'POST':
            if 'PRN_submit' in request.form:
                PRN = request.form['PRN']
                # process form1 data
                with open("WrittenPRN.txt", mode ='w') as file:
                    file.write("Recognized Barcode:" + PRN )
            elif 'register_submit' in request.form:
                name = request.form['Name']
                # process form2 data
                with open("Names.txt", mode ='w') as file:
                    file.write("Recognized Barcode:" + name)
            
        return render_template('index.html')
    
    else:
        # print(barcode_data)
        return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # return a response containing the frames and barcode data from the camera
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # start the Flask app
    app.run(debug=True, threaded=True)
