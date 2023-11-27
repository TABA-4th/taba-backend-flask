# predict.py
import io
import torch
from torchvision import transforms
from PIL import Image
from shared_data import Instance

# 이전에 model1, model2, ..., model6를 로드하던 부분을 함수로 변경
def load_model(model_path):
    return torch.load(model_path, map_location=torch.device('cpu'))  # map_location 변경

if Instance.model_path is not None:
    with open(Instance.model_path, 'rb') as f:
        model1 = torch.load(io.BytesIO(f.read()), map_location='cpu')
        
def predict():
    transform = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 파일 데이터를 메모리에 로드
    file_data_buffer = io.BytesIO(Instance.file_data)
    image = Image.open(file_data_buffer).convert('RGB')
    
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model1(input_tensor)
        _, predicted = torch.max(outputs, 1)
        for i in range(len(Instance.result)):
            Instance.result[i] = predicted[0].item()

