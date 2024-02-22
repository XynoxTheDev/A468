import os
import cv2
import numpy as np
import tensorflow as tf
import plotly.express as px
import matplotlib.pyplot as plt

from tensorflow.keras.preprocessing.image import load_img, img_to_array

model = tf.keras.models.load_model('./numplate_detection.h5')
print('Model loaded Sucessfully')

def object_detection(path):
    # Read image
    image = load_img(path)
    image = np.array(image,dtype=np.uint8)
    image1 = load_img(path,target_size=(224,224))
    
    # Data preprocessing
    image_arr_224 = img_to_array(image1)/255.0
    h,w,d = image.shape
    test_arr = image_arr_224.reshape(1,224,224,3)
    
    # Make predictions
    coords = model.predict(test_arr)
    
    # Denormalize the values
    denorm = np.array([w,w,h,h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    
    # Draw bounding on top the image
    xmin, xmax,ymin,ymax = coords[0]
    pt1 =(xmin,ymin)
    pt2 =(xmax,ymax)
    print(pt1, pt2)
    cv2.rectangle(image,pt1,pt2,(0,255,0),3)
    return image, coords

image, cods = object_detection("tests/c1.jpeg")

