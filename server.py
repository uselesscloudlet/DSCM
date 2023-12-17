import os

import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text

ENGINE = create_engine(
    f"postgresql://{os.environ['user']}:{os.environ['password']}@{os.environ['host']}:{os.environ['port']}/{os.environ['database']}"
)

app = FastAPI()


class Number(BaseModel):
    number: int


@app.post("/check_number/")
async def check_number(request: Number):
    number = request.number
    postgres_connection = ENGINE.connect()
    postgres_connection.execute(
        text("CREATE TABLE IF NOT EXISTS Numbers (number INT);")
    )

    sql_query = f"SELECT * FROM Numbers WHERE number = {number}"
    result = pd.read_sql(sql_query, postgres_connection)

    if len(result > 0):
        raise HTTPException(
            status_code=406, detail=f"Number {number} already is in database"
        )

    sql_query = f"SELECT * FROM Numbers WHERE number = {number + 1}"
    result = pd.read_sql(sql_query, postgres_connection)
    if len(result) > 0:
        raise HTTPException(
            status_code=406, detail=f"Number {number} + 1 already is in database"
        )

    postgres_connection.execute(text(f"INSERT INTO Numbers (number) VALUES ({number})"))

    print(pd.read_sql("SELECT * FROM Numbers", postgres_connection))
    postgres_connection.commit()
    postgres_connection.close()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=f"Added {number} in database"
    )
