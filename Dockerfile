FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput && mkdir -p /data && chown -R 1001:0 /app /data && chmod -R g=u /app /data
ENV DJANGO_DB_PATH=/data/db.sqlite3
USER 1001
EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "django_concert.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
