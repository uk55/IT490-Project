FROM python
COPY . /app
COPY . .
WORKDIR /app
RUN pip3 install -r requirements.txt
ENV FLASK_APP=app.py
CMD ["python", "app.py"]
