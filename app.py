import io
import json
import os
import boto3

import torch
from torchvision import transforms
from PIL import Image
import torchvision.datasets as datasets
from flask import Flask, jsonify, request
from flask_restful import Api
from datetime import datetime
from os import access

# from m_connection import s3_connection, s3_put_object
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY

model_path = 'aram_fine_crust231109.pt'
class_names = [0,1,2,3]

app = Flask(__name__)

# S3에 flask 연결
s3 = boto3.client(
    service_name='s3',
    region_name=AWS_S3_BUCKET_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

model = torch.load(model_path, map_location='cpu')   

transform = transforms.Compose([
    transforms.Resize([224, 224]),  # EfficientNet-b0에 맞는 이미지 사이즈
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def transform_image(file):
    image = Image.open(file).convert('RGB')
    input_tensor = transform(image).unsqueeze(0)  # 이미지를 텐서로 변환하고 배치 차원을 추가합니다.

    return input_tensor

def predict_image(input_tensor):
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted[0]]

    return predicted_class


@app.route('/', methods=['GET'])
def root():
    return jsonify({'msg' : 'Try POSTing to the /predict endpoint with an RGB image attachment'})

@app.route('/imgupload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        new_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.jpeg'
        file.filename = new_filename
        s3.upload_fileobj(file, AWS_S3_BUCKET_NAME, new_filename)
        return 'file uploaded successfully'
    else:
        return 'No file selected', 404

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file is not None:
            input_tensor = transform_image(file)
            predicted_class = predict_image(input_tensor)
            return jsonify({'class': predicted_class})

if __name__ == '__main__':
    app.run()
