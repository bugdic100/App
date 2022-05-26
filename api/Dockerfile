FROM python
ADD . /api
WORKDIR /api
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python api.py
