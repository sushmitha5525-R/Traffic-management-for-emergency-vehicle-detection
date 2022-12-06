from flask import Flask, render_template, request,session,send_from_directory,Response
import os
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
from threading import Thread
from text_to_speech import speak
from MyRecordVideo import  recordVideo
from alarm import alarm
import numpy as np
from time import sleep
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
cameraNumber = 0

def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx,cy

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fimage')
def fimage():
    return render_template('fimage.html')

@app.route('/fvideo')
def fvideo():
    return render_template('fvideo.html')

@app.route('/flive')
def flive():
    return render_template('flive.html')


@app.route('/detectimage')
def detectimage():
    return render_template('detectImage.html')
@app.route('/detectVideo')
def detectVideo():
    return render_template('detectVideo.html')
@app.route('/detectLive')
def detectLive():
    return render_template('detectLive.html')

@app.route('/record')
def record():
    return render_template('record.html')

@app.route('/record1')
def record1():
    recordVideo()
    return render_template('umsg.html', msg='Operation Completed', color='text-success')

@app.route('/VehicleCount')
def VehicleCount():
    return render_template('VehicleCount.html')


@app.route('/fimage1',methods=['POST'])
def fimage1():
    target = os.path.join(APP_ROOT, 'uploads/')
    destination = ''
    filename = ''
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
    path = 'uploads/'+filename
    frame = cv2.imread(path)
    text = pytesseract.image_to_string(frame)
    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html',filename=filename,emotion=text)

@app.route('/detectImage1',methods=['POST'])
def detectImage1():
    al = alarm()
    target = os.path.join(APP_ROOT, 'uploads/')
    destination = ''
    filename = ''
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
    path = 'uploads/'+filename
    frame = cv2.imread(path)
    frame2 = cv2.flip(frame, 1)
    text = pytesseract.image_to_string(frame)
    text2 = pytesseract.image_to_string(frame2)
    print(text2)
    print(text)
    text= text.upper()
    display = ""
    if "POLICE"  in text:
        display="POLICE VEHICLE DETECTED"
        al.detectAlarm()


    if "FIRE" in text:
        display = display +"FIRE ENGINE VEHICLE DETECTED"
        al.detectAlarm()
    if "AMBULANCE" in text:
        display = display +"FIRE ENGINE VEHICLE DETECTED"
        al.detectAlarm()

    if "AMBULANCE" in text2:
        display = display + "AMBULANCE VEHICLE DETECTED"
        al.detectAlarm()

    if len(display) == 0:
        display="NO EMERGENCY VEHICLE DETECTED"
    font = cv2.FONT_HERSHEY_SIMPLEX

    org = (50, 50)
    fontScale = .3
    color = (255, 0, 0)
    thickness = 1
    image = cv2.putText(frame, display, org, font,
                        fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow("hai", image)
    cv2.waitKey(0)
    Thread(target=say_text, args=(text,)).start()
    return render_template('detectImage1.html',filename=filename,emotion=text,display=display)

@app.route('/fvideo1',methods=['POST'])
def fvideo1():
    target = os.path.join(APP_ROOT, 'uploads/')
    destination = ''
    filename = ''
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
    print('uploads/' + filename)
    cam = cv2.VideoCapture('uploads/' + filename)
    cv2.namedWindow("Character Recognition")
    img_counter = 0
    capturedImage = None
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("Character Recognition", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite('uploads/'+img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            capturedImage = img_name
            break
    cam.release()
    cv2.destroyAllWindows()
    if capturedImage==None:
        return render_template('umsg.html', msg='Image not Captured', color='bg-success')
    img = cv2.imread('uploads/' + capturedImage)
    text = pytesseract.image_to_string(img)
    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html', filename=capturedImage, emotion=text)

@app.route('/detectVideo1',methods=['POST'])
def detectVideo1():
    al = alarm()
    target = os.path.join(APP_ROOT, 'uploads/')
    destination = ''
    filename = ''
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
    print('uploads/' + filename)
    cam = cv2.VideoCapture('uploads/' + filename)
    cv2.namedWindow("Character Recognition")
    img_counter = 0
    capturedImage = None
    largura_min = 80  # Largura minima do retangulo
    altura_min = 80  # Altura minima do retangulo
    offset = 6  # Erro permitido entre pixel
    pos_linha = 550  # Posição da linha de contagem
    delay = 60  # FPS do vídeo
    detec = []
    carros = 0
    subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        tempo = float(1 / delay)
        sleep(tempo)
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey, (3, 3), 5)
        img_sub = subtracao.apply(blur)
        dilat = cv2.dilate(img_sub, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
        dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
        contorno, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.line(frame, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
        for (i, c) in enumerate(contorno):
            (x, y, w, h) = cv2.boundingRect(c)
            validar_contorno = (w >= largura_min) and (h >= altura_min)
            if not validar_contorno:
                continue

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centro = pega_centro(x, y, w, h)
            detec.append(centro)
            cv2.circle(frame, centro, 4, (0, 0, 255), -1)

            for (x, y) in detec:
                if y < (pos_linha + offset) and y > (pos_linha - offset):
                    carros += 1
                    # cv2.line(frame, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
                    detec.remove((x, y))
                    # print("car is detected : " + str(carros))

        frame2 = cv2.flip(frame, 1)
        text = pytesseract.image_to_string(frame)
        text2 = pytesseract.image_to_string(frame2)
        print(text2)
        print(text)
        text = text.upper()
        display = ""
        if "POLICE" in text:
            display = "POLICE VEHICLE DETECTED"
            al.detectAlarm()

        if "FIRE" in text:
            display = display + "FIRE ENGINE VEHICLE DETECTED"
            al.detectAlarm()
        if "AMBULANCE" in text:
            display = display + "FIRE ENGINE VEHICLE DETECTED"
            al.detectAlarm()

        if "AMBULANCE" in text2:
            display = display + "AMBULANCE VEHICLE DETECTED "
            al.detectAlarm()
        if "FIRE" in text2:
            display = display + "FIRE ENGINE VEHICLE DETECTED "
            al.detectAlarm()
        if len(display) == 0:
            display = "NO EMERGENCY VEHICLE DETECTED"
        font = cv2.FONT_HERSHEY_SIMPLEX

        org = (50, 50)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2
        image = cv2.putText(frame, display, org, font,
                            fontScale, color, thickness, cv2.LINE_AA)
        cv2.imshow("hai", image)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite('uploads/' + img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            capturedImage = img_name
            break
    cam.release()
    cv2.destroyAllWindows()
    if capturedImage == None:
        return render_template('umsg.html', msg='Image not Captured', color='bg-success')
    img = cv2.imread('uploads/' + capturedImage)
    text = pytesseract.image_to_string(img)

    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html', filename=capturedImage, emotion=text)

@app.route('/VehicleCount1',methods=['POST'])
def VehicleCount1():

    target = os.path.join(APP_ROOT, 'uploads/')
    destination = ''
    filename = ''
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
    print('uploads/' + filename)
    cam = cv2.VideoCapture('uploads/' + filename)
    cv2.namedWindow("Character Recognition")
    img_counter = 0
    capturedImage = None
    largura_min = 80  # Largura minima do retangulo
    altura_min = 80  # Altura minima do retangulo
    offset = 6  # Erro permitido entre pixel
    pos_linha = 550  # Posição da linha de contagem
    delay = 60  # FPS do vídeo
    detec = []
    carros = 0
    subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()

    while True:
        ret, frame1 = cam.read()
        tempo = float(1 / delay)
        sleep(tempo)
        grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey, (3, 3), 5)
        img_sub = subtracao.apply(blur)
        dilat = cv2.dilate(img_sub, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
        dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
        contorno, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
        for (i, c) in enumerate(contorno):
            (x, y, w, h) = cv2.boundingRect(c)
            validar_contorno = (w >= largura_min) and (h >= altura_min)
            if not validar_contorno:
                continue

            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centro = pega_centro(x, y, w, h)
            detec.append(centro)
            cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

            for (x, y) in detec:
                if y < (pos_linha + offset) and y > (pos_linha - offset):
                    carros += 1
                    # cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
                    detec.remove((x, y))
                    # print("car is detected : " + str(carros))

        cv2.putText(frame1, "VEHICLE COUNT : " + str(carros), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        cv2.imshow("Video Original", frame1)
        cv2.imshow("Detectar", dilatada)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite('uploads/' + img_name, frame1)
            print("{} written!".format(img_name))
            img_counter += 1
            capturedImage = img_name
            break
    cam.release()
    cv2.destroyAllWindows()
    if capturedImage == None:
        return render_template('umsg.html', msg='Image not Captured', color='bg-success')
    img = cv2.imread('uploads/' + capturedImage)
    text = pytesseract.image_to_string(img)

    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html', filename=capturedImage, emotion=text)

@app.route('/flive1')
def flive1():
    cam = cv2.VideoCapture(cameraNumber)
    cv2.namedWindow("Character Recognition")
    img_counter = 0
    capturedImage = None
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("Character Recognition", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite('uploads/'+img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            capturedImage = img_name
            break
    cam.release()
    cv2.destroyAllWindows()
    if capturedImage==None:
        return render_template('umsg.html', msg='Process Completed', color='bg-success')
    img = cv2.imread('uploads/' + capturedImage)
    text = pytesseract.image_to_string(img)
    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html', filename=capturedImage, emotion=text)


@app.route('/detectLive1')
def detectLive1():
    al = alarm()
    cam = cv2.VideoCapture(cameraNumber)
    # cv2.namedWindow("Character Recognition")
    img_counter = 0
    capturedImage = None
    largura_min = 80  # Largura minima do retangulo
    altura_min = 80  # Altura minima do retangulo
    offset = 6  # Erro permitido entre pixel
    pos_linha = 550  # Posição da linha de contagem
    delay = 60  # FPS do vídeo
    detec = []
    carros = 0
    subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        tempo = float(1 / delay)
        sleep(tempo)
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey, (3, 3), 5)
        img_sub = subtracao.apply(blur)
        dilat = cv2.dilate(img_sub, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
        dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
        contorno, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.line(frame, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
        for (i, c) in enumerate(contorno):
            (x, y, w, h) = cv2.boundingRect(c)
            validar_contorno = (w >= largura_min) and (h >= altura_min)
            if not validar_contorno:
                continue

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centro = pega_centro(x, y, w, h)
            detec.append(centro)
            cv2.circle(frame, centro, 4, (0, 0, 255), -1)

            for (x, y) in detec:
                if y < (pos_linha + offset) and y > (pos_linha - offset):
                    carros += 1
                    cv2.line(frame, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
                    detec.remove((x, y))
                    # print("car is detected : " + str(carros))

        frame2 = cv2.flip(frame, 1)
        text = pytesseract.image_to_string(frame)
        text2 = pytesseract.image_to_string(frame2)
        print(text2)
        print(text)
        text = text.upper()
        display = ""
        if "POLICE" in text:
            display = "POLICE VEHICLE DETECTED"
            al.detectAlarm()

        if "FIRE" in text:
            display = display + "FIRE ENGINE VEHICLE DETECTED"
            al.detectAlarm()
        if "AMBULANCE" in text:
            display = display + "FIRE ENGINE VEHICLE DETECTED"
            al.detectAlarm()

        if "AMBULANCE" in text2:
            display = display + "AMBULANCE VEHICLE DETECTED "
            al.detectAlarm()

        if len(display) == 0:
            display = "NO EMERGENCY VEHICLE DETECTED"
        font = cv2.FONT_HERSHEY_SIMPLEX

        org = (50, 50)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2

        image = cv2.putText(frame, display, org, font,
                            fontScale, color, thickness, cv2.LINE_AA)
        cv2.imshow("hai", image)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite('uploads/'+img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            capturedImage = img_name
            break
    cam.release()
    cv2.destroyAllWindows()
    if capturedImage==None:
        return render_template('umsg.html', msg='Process Completed', color='bg-success')
    img = cv2.imread('uploads/' + capturedImage)
    text = pytesseract.image_to_string(img)
    Thread(target=say_text, args=(text,)).start()
    return render_template('fimage1.html', filename=capturedImage, emotion=text)


@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory("uploads", filename)

@app.route('/images/<filename>')
def send_image2(filename):
    return send_from_directory("images", filename)

def say_text(text):
	speak(text)

if __name__ == '__main__':
    app.run(debug=True)
    pass
