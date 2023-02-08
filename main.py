import pymysql
from app import app
from config import mysql
from flask import jsonify, redirect, request, url_for


# ham tra ve ket qua neu loi....
@app.errorhandler(404)
def showMessage(error=None):
    message = {
        "status": 404,
        "message": "Record not found: " + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone


# chuyen ve ham user neu khong nhap gi
@app.route("/")
def index():
    return redirect(url_for("users"))


def getjsondata(json):
    name = "None"
    email = "None"
    phone = "None"
    address = "None"
    if json:
        name = json["name"]
        email = json["email"]
        phone = json["phone"]
        address = json["address"]
    return name, email, address, phone


# ham tao du lieu moi cho database
@app.route("/create", methods=["POST"])
def create_emp():
    # khoi tao du lieu nhan duoc tu postman dang json
    json = request.get_json()
    # gui du lieu len db
    if json and request.method == "POST":
        # ket noi voi db
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _name, _email, _phone, _address = getjsondata(json)
        sqlQuery = "INSERT INTO emp(name, email, phone, address) VALUES(%s, %s, %s, %s)"
        bindData = (_name, _email, _phone, _address)
        # execute chap nhan db duoc thay doi theo lenh va cac du lieu vao
        cursor.execute(sqlQuery, bindData)
        # luu thay doi du lieu tren db
        conn.commit()
        # tra ve ket qua
        respone = jsonify("Employee added successfully!")
        respone.status_code = 200
        return respone
    else:
        return showMessage()
    cursor.close()
    conn.close()


# ham doc lu lieu cua db
@app.route("/users", methods=["GET"])
def users():
    if request.method == "GET":
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, name, email, phone, address FROM emp")
        # fetchall la lay tat ca du lieu co trong db
        empRows = cursor.fetchall()
        respone = jsonify(empRows)
        respone.status_code = 200
        return respone
    cursor.close()
    conn.close()


# ham doc du lieu cua rieng 1 id trong db
@app.route("/user", methods=["GET"])
def getuserbyid():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # thuc hien truy van lay du lieu nhap vao tu postman( ?id= )
    _id = request.args.get("id")
    print(_id)
    # lay du lieu trong db voi id = _id
    cursor.execute("SELECT id, name, email, phone, address FROM emp WHERE id =%s", _id)
    # fetchone la lay du lieu co id = _id va lay du lieu lien ke duy nhat
    empRow = cursor.fetchone()
    # tra ve "khong co du lieu" neu khong tim thay id
    if empRow is None:
        respone = jsonify("khong co du lieu")
    else:
        respone = jsonify(empRow)
    respone.status_code = 200
    return respone


# ham thay doi thong tin cua du lieu trong db
@app.route("/update", methods=["PUT"])
def update_emp():
    # doc du lieu de thay doi , du lieu duoc gui len tu postman
    _json = request.json
    _id = _json["id"]
    _name = _json["name"]
    _email = _json["email"]
    _phone = _json["phone"]
    _address = _json["address"]
    # print(_id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM emp")
    dsid = cursor.fetchall()
    # kiem tra xem _id dua vao co trong db hay khong
    k = 0
    for ds in dsid:
        if _id == ds[0]:
            k = k + 1
    # neu id co trong db thi bat dau qua trinh update, neu khong thi tra ve "khong co du lieu"
    if (
        k == 1
        and _name
        and _email
        and _phone
        and _address
        and _id
        and request.method == "PUT"
    ):
        # thay doi du lieu cu bang du lieu doc duoc
        # chi thay doi cho id da doc duoc trong du lieu gui len
        sqlQuery = "UPDATE emp SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s"
        bindData = (
            _name,
            _email,
            _phone,
            _address,
            _id,
        )
        cursor.execute(sqlQuery, bindData)
        # luu thay doi du lieu trong db
        conn.commit()
        respone = jsonify("Employee updated successfully!")
        respone.status_code = 200
        return respone
    else:
        respone1 = jsonify("khong ton tai id")
        return respone1

    cursor.close()
    conn.close()


# ham xoa du lieu trong db
@app.route("/delete", methods=["DELETE"])
def deleteusers():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # thuc hien truy van du lieu voi id = (?id=), co the thay the = name ,address, phone , ...
    _id = request.args.get("id")
    # xoa du lieu trong db voi id = _id
    cursor.execute("DELETE FROM emp WHERE id =%s", _id)
    # luu thay doi trong db
    conn.commit()
    respone = jsonify("Delete successful!")
    respone.status_code = 200
    return respone
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # chay chuong trinh voi may chu 127.0.0.1(localhost), port=6969
    app.run(host="127.0.0.1", port=6969, debug=True)
