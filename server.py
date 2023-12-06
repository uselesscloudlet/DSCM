import configparser

import pandas as pd
import vertica_python
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine

config = configparser.ConfigParser()
config.read("config.cfg")

CONNECTION_INFO = dict(config.items("DB_CONNECTION"))

ENGINE = create_engine(
    f"vertica+vertica_python:/{CONNECTION_INFO['user']}:{CONNECTION_INFO['password']}@{CONNECTION_INFO['host']}:{CONNECTION_INFO['port']}/{CONNECTION_INFO['database']}"
)

app = FastAPI()


class Number(BaseModel):
    number: int


@app.post("/check_number/")
async def check_number(request: Number):
    number = request["number"]
    vertica_connection = vertica_python.connect(CONNECTION_INFO)
    sql_query = f"SELECT * FROM Scheme.Table WHERE number = {number}"
    result = pd.read_sql(sql_query, vertica_connection)

    if len(result > 0):
        raise HTTPException(
            status_code=406, detail=f"Number {number} already is in database"
        )

    sql_query = f"SELECT * FROM Scheme.Table WHERE number = {number + 1}"
    result = pd.read_sql(sql_query, vertica_connection)
    if len(result) > 0:
        raise HTTPException(
            status_code=406, detail=f"Number {number} + 1 already is in database"
        )

    new_value = pd.DataFrame({"number": [number]})

    new_value.to_sql(
        "Table", schema="Scheme", con=ENGINE, if_exists="append", index=False
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content=number)
