import sys
import json
import psycopg2

from PyQt5 import QtWidgets
from hierarchDataCollectionUI import Ui_Form


# Функция обработки нажатия на кнопку
def btnClicked():
    conn = psycopg2.connect(dbname='Department',
                            user='admin',
                            password='admin',
                            host='localhost')
    cursor = conn.cursor()
    importData("data.json", cursor)
    getEmployeesList(cursor)
    cursor.close()
    conn.close()

# Функция для выполнения запросов в базу данных и получения списка сотрудников
def getEmployeesList(cursor):
    inputedId = ui.spinBox.text()
    cursor.execute("SELECT id FROM employee WHERE id=" + inputedId)
    idExist = cursor.fetchall()
    if idExist:
        try:
            cursor.execute("""SELECT id, name FROM employee WHERE type=1 AND id <= """ + inputedId)
        except Exception as e:
            print(e.pgerror)

        records = cursor.fetchall()
        if records:
            lowBorder = records[-1][0]
        else:
            lowBorder = "MIN(id)"

        office = records[-1][1]
        try:
            cursor.execute("""SELECT id FROM employee WHERE type=1 AND id > """ + inputedId)
        except Exception as e:
            print(e.pgerror)

        records = cursor.fetchall()
        if records:
            topBorder = records[0][0]
        else:
            topBorder = "MAX(id)"

        try:
            cursor.execute(
                            """SELECT name FROM employee WHERE type=3
                            GROUP BY id, name HAVING id BETWEEN {} AND {}"""
                            .format(lowBorder, topBorder))
            records = cursor.fetchall()
        except Exception as e:
            print(e.pgerror)
        result = ""
        for i in range(len(records)):
            result += str(records[i][0]) + "\n"
        result = "    " + office + ":\n" + result
        ui.textBrowser.setText(result)
    else:
        ui.textBrowser.setText("Такого id не существует!")

# Функция для имортирования данныйх из файла data.json в базу данных
def importData(fileName, cursor):
    filePath = fileName
    with open(filePath, 'r', encoding="utf-8") as f:
        fileData = json.load(f)
    for idx, val in enumerate(fileData):
        try:
            if val["ParentId"] == None:
                val["ParentId"] = "NULL"
            cursor.execute("""INSERT INTO employee (id, parentid, name, type)
                                VALUES({}, {}, '{}', {});"""
                           .format(val["id"], val["ParentId"], val["Name"], val["Type"]))
        except Exception as e:
            print(e.pgerror)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    ui.pushButton.clicked.connect(btnClicked)
    sys.exit(app.exec_())