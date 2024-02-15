import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

image_path = 'tests/g1.png'
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

boxes, _ = mtcnn.detect(image)

if boxes is not None:
    for box in boxes:
        x_center = (box[0] + box[2]) // 2
        y_center = (box[1] + box[3]) // 2
        width = int((box[2] - box[0]) * 1.5)
        height = int((box[3] - box[1]) * 1.4)
        
        x1 = max(0, int(x_center - width // 2))
        y1 = max(0, int(y_center - height // 2))
        x2 = min(image.shape[1], int(x_center + width // 2))
        y2 = min(image.shape[0], int(y_center + height // 2))
        
        expanded_box = [x1, y1, x2, y2]
        
        face = image[expanded_box[1]:expanded_box[3], expanded_box[0]:expanded_box[2]]
        blurred_face = cv2.GaussianBlur(face, (99, 99), 30)  # Adjust sigma value as needed
        image[expanded_box[1]:expanded_box[3], expanded_box[0]:expanded_box[2]] = blurred_face
else:
    print("No faces detected in the image.")

cv2.imshow('Faces', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
cv2.destroyAllWindows()
