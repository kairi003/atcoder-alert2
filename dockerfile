FROM python:3.9

ENV TZ=Asia/Tokyo
ENV WEBHOOK=https://discord.com/api/webhooks/

ADD files/* /root/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /root/requirements.txt

CMD ["python3", "/root/atcoder_alert.py"]