import pandas as pd
import vertica_python
import requests
from sqlachemy import create_engine


class DigitChecker:
    def __init__(self):
        self.__connection_info = {
            "host": "host",
            "port": 5433,
            "database": "BD",
            "user": "user",
            "password": "password",
            "read_timeout": 600,
            "unicode_error": "strict",
            "ssl": False,
        }
        self.__engine = create_engine(
            "vertica+vertica_python:/user:password@host:5433/BD"
        )

    def check_number(self, request):
        number = request.data
        vertica_connection = vertica_python.connect(self.__connection_info)
        sql_query = f"SELECT * FROM Scheme.Table WHERE number = {number}"
        result = pd.read_sql(sql_query, vertica_connection)

        if len(result > 0):
            return "Введенное число уже есть в БД"

        sql_query = f"SELECT * FROM Scheme.Table WHERE number = {number + 1}"
        result = pd.read_sql(sql_query, vertica_connection)
        if len(result) > 0:
            return "Поступало число на 1 больше"

        new_value = pd.DataFrame({"number": [number]})

        new_value.to_sql("Table", schema="Scheme", con=self.__engine, if_exists="append", index=False)

        return number
    
dc = DigitChecker()
while True:
    host = "http://localhost:8000"
    request = requests.get(host)
    response = dc.check_number(request)
    requests.post(host, data=response)
