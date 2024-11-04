FROM python:3.9

WORKDIR /code

# requirements.txt faylini konteyner ichiga nusxalash
RUN apt-get update && apt-get install -y libreoffice
COPY ./requirements.txt /code/requirements.txt

# Barcha kerakli kutubxonalarni o'rnatish
RUN pip install --no-cache-dir -r /code/requirements.txt

# Loyihangizni nusxalash
COPY ./ /code/

# Konteynerda bajariladigan buyruq
CMD python app.py & python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

