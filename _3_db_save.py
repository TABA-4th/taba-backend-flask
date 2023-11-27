# _3_db_save.py
import pyodbc
from datetime import datetime
from config import user, passwd
from shared_data import Instance

def db_save():
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
    
        # result_id 1 증가
        result_id = max_result_id + 1 if max_result_id is not None else 1

        # 사용자 ID, 모델 출력 결과, 날짜를 저장하는 쿼리
        sql = "INSERT INTO diagnosis_result (RESULT_ID, MEMBER_ID, DIAGNOSIS_DATE, FINE_DEAD_SKIN_CELLS, EXCESS_SEBUM, ERYTHEMA_BETWEEN_HAIR_FOLLICLES, DANDRUFF, HAIR_LOSS, ERYTHEMA_PUSTULES, IMAGE_URL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (result_id, Instance.member_id, Instance.db_time, Instance.result[0], Instance.result[1], Instance.result[2], Instance.result[3], Instance.result[4], Instance.result[5], Instance.image_url)
        curs.execute(sql, values)
    
        conn.commit()
        conn.close()

    except Exception as ex:
        print(ex)
