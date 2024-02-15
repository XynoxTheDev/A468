import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

# Load pre-trained models
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Load image
image_path = 'tests/1.jpg'
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Detect faces
boxes, _ = mtcnn.detect(image)

# Identify faces
if boxes is not None:
    for box in boxes:
        box = box.astype(int)
        face = image[box[1]:box[3], box[0]:box[2]]
        face = cv2.resize(face, (160, 160))
        face_tensor = torch.tensor(face).permute(2, 0, 1).unsqueeze(0).float().to(device)
        
        embedding = resnet(face_tensor).detach().cpu().numpy().flatten()
        
        print("Face Embedding:", embedding)
else:
    print("No faces detected in the image.")
