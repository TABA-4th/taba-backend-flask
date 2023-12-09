import io
import torch
from torchvision import transforms
from PIL import Image
from shared_data import Instance
import torchvision.transforms.functional as TF


def validate_image():
    transforms_train = transforms.Compose([ 
    transforms.Resize([224, 224], interpolation=transforms.InterpolationMode.BICUBIC),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 파일 데이터를 메모리에 로드
    file_data_buffer = io.BytesIO(Instance.file_data)
    image = Image.open(file_data_buffer).convert('RGB')
    input_tensor = transforms_train(image).unsqueeze(0)

    model = torch.load(Instance.validation_model_path, map_location=torch.device('cpu'))
    model.eval()

    # 예측 수행
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)

        result = predicted.item()

    return result