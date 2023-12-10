# _3_db_save_image.py
import pyodbc
from datetime import datetime
from pytz import timezone
from config import user, passwd
from shared_data import Instance

def db_save_image():
    try:
        result_id = int(Instance.url_time)

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

        # 사용자 닉네임에 해당하는 member_id 찾기
        curs.execute("""SELECT MEMBER_ID 
                                  FROM MEMBER 
                                  WHERE NICKNAME = ? ;""", Instance.member_nickname)
        Instance.member_id = curs.fetchone()[0]
    
        # result_id 1 증가
        result_id = max_result_id + 1 if max_result_id is not None else 1

        # db에 저장할 시간
        Instance.db_time = Instance.now.strftime('%Y-%m-%d %H:%M:%S')

        topPercentage = ' '.join(map(str, Instance.member_percentile))

        # 사용자 ID, 모델 출력 결과, 날짜를 저장하는 쿼리
        sql = "INSERT INTO diagnosis_result (RESULT_ID, MEMBER_ID, DIAGNOSIS_DATE, FINE_DEAD_SKIN_CELLS, EXCESS_SEBUM, ERYTHEMA_BETWEEN_HAIR_FOLLICLES, DANDRUFF, HAIR_LOSS, ERYTHEMA_PUSTULES, IMAGE_URL, TOP_PERCENTAGE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (result_id, Instance.member_id, Instance.db_time, Instance.result[0], Instance.result[1], Instance.result[2], Instance.result[3], Instance.result[4], Instance.result[5], Instance.image_url, topPercentage)
        curs.execute(sql, values)
    
        conn.commit()
        conn.close()

    except Exception as ex:
        print(ex)
