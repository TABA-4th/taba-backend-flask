import io
import torch
from torchvision import transforms
from PIL import Image
from shared_data import Instance

def predict(idx):
    transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomRotation(20),
    transforms.RandomAffine(0, shear=15, scale=(0.8, 1.2)),
    transforms.Resize([int(224), int(224)], interpolation=4),
    transforms.ToTensor(),
    transforms.Lambda(random_transforms),
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

        # 특정 모델에 대한 조건적 처리
        if idx in [0, 1] and predicted[0].item() in [1, 2]:
            Instance.result[idx] = 1.5
        else:
            Instance.result[idx] = predicted[0].item()