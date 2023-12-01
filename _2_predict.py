import io
import torch
from torchvision import transforms
from PIL import Image
from shared_data import Instance

def predict(idx):
    transform = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 파일 데이터를 메모리에 로드
    file_data_buffer = io.BytesIO(Instance.file_data)
    image = Image.open(file_data_buffer).convert('RGB')
    input_tensor = transform(image).unsqueeze(0)

    # idx에 해당하는 모델 로드
    x = getattr(Instance, f"model_path{idx}")
    if x is not None:
        with open(x, 'rb') as f:
            model = torch.load(io.BytesIO(f.read()), map_location='cpu')

    # 모델을 평가 모드로 설정
    model.eval()

    # 예측 수행
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        Instance.result[idx] = predicted[0].item()