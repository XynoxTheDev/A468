from flask import Flask, request, render_template, send_file, make_response, jsonify
from mtcnn import FaceModel
from numplate_model import NumplateModel
import cv2
from io import BytesIO
import numpy as np

app = Flask(__name__)
face_model = FaceModel()
plate_model = NumplateModel('./numplate_detection.h5')

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    try:
        if file:
            # file.save(file.filename)
            face = request.form.get('face')
            numplate = request.form.get('numplate')
            image_stream = BytesIO()
            nparr = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if face is not None:
                image = face_model.detect(image)
            if numplate is not None:
                image = plate_model.detect(image)
            success, encoded_image = cv2.imencode('.jpg', image)
            if success:
                image_stream.write(encoded_image.tobytes())
                image_stream.seek(0)
                response = make_response(send_file(image_stream, mimetype='image/jpeg'))
                response.headers['Content-Disposition'] = f'attachment; filename={file.filename}'
                return response

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
