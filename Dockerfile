FROM python:3.11.7

WORKDIR /usr/src/app
RUN pip install poetry

COPY . .
RUN poetry update && poetry install 
ENTRYPOINT ["poetry", "run", "uvicorn", "api:app", "--reload", "--host", "0.0.0.0"]
