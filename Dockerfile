FROM python:3.11.4

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8000

ENTRYPOINT ["./deploy.sh"]
