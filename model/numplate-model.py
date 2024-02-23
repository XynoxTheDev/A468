import os
import cv2
import numpy as np
import tensorflow as tf
import plotly.express as px
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array

class NumplateModel:
    def __init__(self, trained_weights_path):
        self.model = tf.keras.models.load_model(trained_weights_path)
    # model = tf.keras.models.load_model('')

    def detect(self, image_data):
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        image1 = cv2.resize(image, (224, 224))
        image = np.array(image,dtype=np.uint8) # 8 bit array (0,255)
        
        # Data preprocessing
        image_arr_224 = img_to_array(image1)/255.0 # Convert to array & normalized
        h,w,d = image.shape
        test_arr = image_arr_224.reshape(1,224,224,3)
        
        # Make predictions
        coords = self.model.predict(test_arr)
        
        # Denormalize the values
        denorm = np.array([w,w,h,h])
        coords = coords * denorm
        coords = coords.astype(np.int32)[0]
        coords = ((coords[0], coords[2]), (coords[1], coords[3]))
        return self.apply_blur(image, coords)

    def apply_blur(self, image, coords):
        tl, br = coords
        center_x = (tl[0] + br[0]) // 2
        center_y = (tl[1] + br[1]) // 2

        nw = int((br[0] - tl[0]) * 2)  # new_width
        nh = int((br[1] - tl[1]) * 2)  # new_height

        new_tl = (center_x - nw // 2, center_y - nh // 2)
        new_br = (center_x + nw // 2, center_y + nh // 2)

        mask = image.copy()
        cv2.rectangle(mask, new_tl, new_br, (255, 255, 255), -1)
        blurred_region = cv2.GaussianBlur(image[new_tl[1]:new_br[1], new_tl[0]:new_br[0]], (25, 25), 10)
        result = cv2.bitwise_and(image, mask)
        result[new_tl[1]:new_br[1], new_tl[0]:new_br[0]] = blurred_region
        return result

if __name__ == "__main__":
    image_path = 'tests/c1.jpeg'
    file = open(image_path, 'rb')
    plate = NumplateModel('./numplate_detection.h5')
    image = plate.detect(file.read())
    cv2.imshow('Blured', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

