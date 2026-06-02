FROM python:3.13.7
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "smart_property_finder.wsgi:application"]
