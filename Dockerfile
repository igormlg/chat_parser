FROM python:3

COPY . .

WORKDIR /

RUN pip3 install python-dotenv && pip3 install Telethon && pip3 install aiogram

ENTRYPOINT [ "python", "chat_parser.py" ]