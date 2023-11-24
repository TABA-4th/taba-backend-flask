import io
import re
from datetime import datetime
import boto3
import pyodbc

import torch
from torchvision import transforms
from PIL import Image
from flask import Flask, jsonify, request, session
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, user, passwd

now = datetime.now()
member_id = 4 # 임시로 4로 설정

url_time = re.sub(r"[^0-9]", "", str(now))
db_time = now.strftime('%Y-%m-%d %H:%M:%S')

model_path = 'aram_fine_crust231109.pt'
class_names = [0, 1, 2, 3]

app = Flask(__name__)

# S3-Flask Connect
s3 = boto3.client(
    service_name='s3',
    region_name=AWS_S3_BUCKET_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Model
model = torch.load(model_path, map_location='cpu')

# Preprocessing
transform = transforms.Compose([
    transforms.Resize([224, 224]),  # EfficientNet-b0에 맞는 이미지 사이즈
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def transform_image(file_data):
    image = Image.open(io.BytesIO(file_data)).convert('RGB')
    input_tensor = transform(image).unsqueeze(0)
    return input_tensor

# Prediction
def predict_image(input_tensor):
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted[0]]
    return predicted_class


@app.route('/', methods=['GET'])
def root():
    return jsonify({'msg': 'Try POSTing to the /predict endpoint with an RGB image attachment'})

@app.route('/predict', methods=['POST'])
def predict():

    if 'file' not in request.files:
        return 'No file part', 400
    file_data = request.files['file'].read()
    if not file_data:
        return 'No file data', 400
    
    # S3에 이미지 업로드
    new_filename = url_time + '.jpeg'
    s3.upload_fileobj(io.BytesIO(file_data), AWS_S3_BUCKET_NAME, new_filename)
    image_url = f'https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{new_filename}'
    image_url = str(image_url)

    # 이미지 예측
    input_tensor = transform_image(file_data)
    predicted_class = predict_image(input_tensor)

    # DB에 결과 데이터 저장
    try:
        result_id = int(url_time)

        conn = pyodbc.connect('DSN=tibero;UID='+user+';PWD='+passwd)
        conn.setdecoding(pyodbc.SQL_CHAR, encoding='euc-kr')
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='euc-kr')
        conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='euc-kr')
        conn.setencoding(encoding='utf-8')
        curs = conn.cursor()

        # 현재 저장된 최대 result_id 가져오기
        max_result_id_query = "SELECT MAX(RESULT_ID) FROM diagnosis_result;"
        curs.execute(max_result_id_query)
        max_result_id = curs.fetchone()[0]
    
        # result_id 1 증가
        result_id = max_result_id + 1 if max_result_id is not None else 1

        # 사용자 ID, 모델 출력 결과, 날짜를 저장하는 쿼리
        sql = "INSERT INTO diagnosis_result (RESULT_ID, MEMBER_ID, DIAGNOSIS_DATE, FINE_DEAD_SKIN_CELLS, EXCESS_SEBUM, ERYTHEMA_BETWEEN_HAIR_FOLLICLES, DANDRUFF, HAIR_LOSS, ERYTHEMA_PUSTULES, IMAGE_URL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (result_id, member_id, db_time, predicted_class, predicted_class, predicted_class, predicted_class, predicted_class, predicted_class, image_url)
        curs.execute(sql, values)
    
        conn.commit()
        conn.close()

    except Exception as ex:
        print(ex)
    
    return jsonify({'class': predicted_class, 'url': image_url, 'msg': 'Data saved to database successfully'})

if __name__ == '__main__':
    app.run(debug=True)

