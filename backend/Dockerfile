FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# A chave abaixo existe só durante o build, para o collectstatic carregar as configurações.
# A chave real fica na variável DJANGO_SECRET_KEY do serviço.
RUN DJANGO_SECRET_KEY=somente-para-o-build python manage.py collectstatic --noinput

EXPOSE 8000

# As migrações rodam a cada início, antes do servidor, para o banco acompanhar o código publicado.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind [::]:${PORT:-8000} --workers ${GUNICORN_WORKERS:-2} --timeout 120 --access-logfile -"]
