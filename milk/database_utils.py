# database_utils.py

import mysql.connector
from mysql.connector import Error

# 데이터베이스에 연결하는 함수
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="milk_detect"
        )
        print("MySQL 연결 성공")
        return connection
    except Error as e:
        print("MySQL 연결 오류:", e)
        return None

# 바이너리 형식으로 이미지 파일을 읽는 함수
def read_image_as_blob(image_path):
    try:
        with open(image_path, "rb") as file:
            binary_data = file.read()
        return binary_data
    except Exception as e:
        print(f"이미지 파일을 읽는 중 오류 발생: {e}")
        return None

# 데이터베이스에 우유팩 정보 저장
def save_milk_info(connection, text, color, width, height, image_blob):
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO milks (text, color, width, height, image)
            VALUES (%s, %s, %s, %s, %s)
        """
        data_values = (text, color, width, height, image_blob)
        cursor.execute(insert_query, data_values)
        connection.commit()
        print("우유팩 정보가 성공적으로 데이터베이스에 저장되었습니다.")
    except Error as e:
        print("데이터 저장 오류:", e)

# 데이터베이스에서 특정 우유팩 정보 조회
def get_milk_info(connection, text):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM milks WHERE text = %s"
        cursor.execute(query, (text,))
        result = cursor.fetchone()
        if result:
            print("데이터베이스에서 찾은 우유팩 정보:", result)
            return result
        else:
            print("데이터베이스에서 해당 우유팩 정보를 찾지 못했습니다.")
            return None
    except Error as e:
        print("데이터 조회 오류:", e)
        return None


def fetch_milk_info(connection, width, height, color):
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT text FROM milk_Info 
    WHERE width = %s AND height = %s AND color = %s
    """
    cursor.execute(query, (width, height, color))
    result = cursor.fetchone()
    cursor.close()
    return result