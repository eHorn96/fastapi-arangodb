FROM python:3.12

LABEL author="Erik Horn, 60439 Frankfurt am Main"

WORKDIR /app
RUN apt update
RUN apt upgrade -y
COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN pip install -r requirements.txt
COPY ./ ./

EXPOSE 8080

RUN useradd fastapi
RUN chown -R fastapi:fastapi /app
USER fastapi

CMD ["uvicorn", "main:app", "--port","8080", "--host", "0.0.0.0", "--reload"]
