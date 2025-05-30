FROM python:alpine

WORKDIR /rebalancer

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "-u", "run.py"]