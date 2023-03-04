from flask import Flask, render_template, Response, request, session
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')

if not os.path.exists('staticFiles'):
    os.makedirs('staticFiles')
app = Flask(__name__, template_folder='templates', static_folder='staticFiles/')
app.config['UPLOAD_FOLDER'] = 'staticFiles/'
app.secret_key = 'MLS-Cartoonify-App'


@app.route("/")
def index():
  return render_template('index.html')


@app.route('/', methods=('POST', 'GET'))
def uploadFile():
  global img_filename
  if request.method == 'POST':
    uploaded_img = request.files['uploaded-file']
    img_filename = secure_filename(uploaded_img.filename)
    uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    
    cartooned_img = cartoonify(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], img_filename), cartooned_img)
    # Storing uploaded file path in flask session
    #session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
    session['uploaded_img_file_path'] = os.path.join('staticFiles', img_filename)
    img_file_path = session.get('uploaded_img_file_path', None)
    return render_template('index_uploaded.html')


@app.route('/show_image')
def displayImage():  # Retrieving uploaded file path from session
  #img_file_path = session.get('uploaded_img_file_path')
  img_file_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
  # Display image in Flask application web page
  return render_template('show_image.html', user_image = img_file_path)
  #return render_template('show_image.html', user_image=os.path.join(app.config['UPLOAD_FOLDER'], img_filename))


def cartoonify(image):
  originalImage = cv2.imread(image)
  originalImage = cv2.resize(originalImage, (640,480))
  grayScaleImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
  smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
  getEdge = cv2.adaptiveThreshold(smoothGrayScale, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
  
  data = np.float32(originalImage).reshape((-1,3))
  criteria = (cv2.TERM_CRITERIA_EPS+ cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
  ret, label, center = cv2.kmeans(data, 4, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
  center = np.uint8(center)
  result=center[label.flatten()]
  result = result.reshape(originalImage.shape)
  
  colorImage = cv2.bilateralFilter(result, 9, 300, 300)
 
  cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=getEdge)

  ReSized6 = cv2.resize(cartoonImage, (960, 540))
  return ReSized6


if __name__=='__main__':
  app.run(host='127.0.0.0', port=8888, debug=True)
