import mysql.connector

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="milk_detect"
)
cursor = db_connection.cursor()

def convert_to_binary(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

def insert_milk_data(text, color, width, height, image_path):
    binary_image = convert_to_binary(image_path)
    sql = "INSERT INTO Milks_Info (text, color, width, height, image) VALUES (%s, %s, %s, %s, %s)"
    data = (text, color, width, height, binary_image)
    cursor.execute(sql, data)
    db_connection.commit()
    print("Data and image inserted successfully.")

insert_milk_data("흰우유", "white", 250, 300, "/home/pi/webapps/CoinProject/imageMilk/green.jpg")


cursor.close()
db_connection.close()
