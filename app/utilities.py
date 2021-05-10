import re
import pymysql
import time


def check_email(email):
    c = re.compile(r'^\w+@(\w+\.)+(com|cn|net)$')
    s = c.search(email)
    if s:
        return True
    else:
        return False


def create_user(username, password, email, gender, age, occupation):
    register_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = "INSERT INTO app_user (username,age,gender,occupation,profile_pic,password,register_time,email) values" \
          "  (%s,%s,%s,%s,%s,%s,%s,%s);"
    cursor.execute(sql,
                   [username, age, gender, occupation, None, password, register_time, email])
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    print('utilities')