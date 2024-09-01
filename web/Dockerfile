FROM php:8.2-apache
#apachectl restart
RUN apt-get update && apt-get install -y curl
RUN docker-php-ext-install mysqli
COPY . /var/www/html/
EXPOSE 80

