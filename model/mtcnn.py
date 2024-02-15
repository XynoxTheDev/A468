import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

image_path = 'tests/1.jpg'
image = cv2.imread(image_path)

boxes, _ = mtcnn.detect(image)

if boxes is not None:
    for box in boxes:
        x_center = (box[0] + box[2]) // 2
        y_center = (box[1] + box[3]) // 2
        width = int((box[2] - box[0]) * 2)
        height = int((box[3] - box[1]) * 2)
        
        x1 = max(0, int(x_center - width // 2))
        y1 = max(0, int(y_center - height // 2))
        x2 = min(image.shape[1], int(x_center + width // 2))
        y2 = min(image.shape[0], int(y_center + height // 2))
        
        expanded_box = [x1, y1, x2, y2]
        
        face = image[expanded_box[1]:expanded_box[3], expanded_box[0]:expanded_box[2]]
        blurred_face = cv2.GaussianBlur(face, (99, 99), 30)  # Adjust sigma value as needed
        s_height, s_width, _ = face.shape
        mask = np.full((s_height, s_width), 0, dtype=np.uint8)
        cv2.ellipse(mask, (s_width // 2, s_height // 2), (s_width // 2, s_height // 2), 0, 0., 360, (255, 25, 255), -1)

        masked_image1 = cv2.bitwise_and(blurred_face, blurred_face, mask = mask)

        inverse_mask = cv2.bitwise_not(mask)

        masked_image2 = cv2.bitwise_and(face, face, mask = inverse_mask)
        combined_image = cv2.add(masked_image1, masked_image2)

        image[expanded_box[1]:expanded_box[3], expanded_box[0]:expanded_box[2]] = combined_image
        print(x_center, y_center)
else:
    print("No faces detected in the image.")

cv2.imshow('Faces', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
