FROM python:3
WORKDIR /app
COPY ./ /app/
RUN python -m pip install -r ./requirements.txt
CMD python main.py