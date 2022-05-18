FROM python:3.8
RUN pip install flask==2.1.2
RUN useradd -ms /bin/bash admin
USER admin
WORKDIR /app
COPY app /app
CMD ["python","app.py"]
