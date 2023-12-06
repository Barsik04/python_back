from flask import Flask, request, jsonify
import hashlib
import psycopg2

db_host = 'postgres'  # Replace with your PostgreSQL host
db_name = 'rfid'  # Replace with your PostgreSQL database name
db_user = 'rfid_user'  # Replace with your PostgreSQL username
db_password = 'rfid_user_password'  # Replace with your PostgreSQL password
db_port = '5432'  # Replace with your PostgreSQL port number (usually 5432)

# SQL-запрос для вставки строки в таблицу users
sql = """INSERT INTO users (id, surname, name, second_name, dob)
         VALUES (%s, %s, %s, %s, %s);"""

app = Flask(__name__)


def calculate_hash(str):
    hasher = hashlib.sha256()
    hasher.update(str)
    return hasher.hexdigest()


# Обработчик для записи сообщения в базу данных и отправки ответа клиенту
@app.route('/create_user', methods=['POST'])
def create_user():
    json_data = request.get_json()
    # print(json_data)

    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port  # Порт PostgreSQL (обычно 5432)
        )
        cursor = connection.cursor()

        if cursor:
            hashSum = calculate_hash(
                bytearray(json_data['name'] + json_data['second_name'] + json_data['surname'] + json_data['dob'],
                          encoding='utf8'))
            data = (str(hashSum), json_data['surname'], json_data['name'], json_data['second_name'], json_data['dob'])
            cursor.execute(sql, data)
            connection.commit()
            print("Data inserted successfully into users table!")
            print("created " + hashSum)
            response = {'status': 'created', 'id': str(hashSum)}
            connection.close()

        return jsonify(response)
    except psycopg2.Error as e:
        if e.pgcode == '23505':
            response = {'status': 'Error', 'message': "Пользователь существует"}
            return jsonify(response)
        return jsonify({'status': 'error', 'message':str(e)})
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response)




@app.route('/check_authorization', methods=['GET'])
def wsanother_endpoint():
    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
        )
        cursor = connection.cursor()
        status = "Undefined"
        if cursor:
            args = request.args
            data = args.get("id", default="", type=str)

            print(data)
            query = """SELECT * FROM users WHERE id = %s;"""
            cursor.execute(query, (data,))
            rows = cursor.fetchall()

            if len(rows) != 0:
                status = "Доступ разрешен"
            else:
                status = "Доступ запрещен"
        connection.close()
        print(status)
        response = {'status': status}
        return jsonify(response)

    except Exception as e:
        print(e)
        response = {'status': 'error', 'message': str(e)}

    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
