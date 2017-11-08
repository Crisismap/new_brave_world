FROM python:2.7.13-jessie

ADD ./requirements.txt /app/

RUN pip install -r /app/requirements.txt
ADD ./ /app/

CMD python /app/web_run.py

