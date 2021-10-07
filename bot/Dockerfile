FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /server
WORKDIR /server
COPY requirements.txt /server/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /server/ 
EXPOSE 8000

# CMD gunicorn app.wsgi:application --bind 0.0.0.0:8000