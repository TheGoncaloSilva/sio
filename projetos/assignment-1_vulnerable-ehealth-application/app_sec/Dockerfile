FROM php:8.0-apache
RUN apt-get update -y && apt-get install -y libmariadb-dev
RUN docker-php-ext-install mysqli

RUN a2enmod rewrite && a2enmod ssl && a2enmod socache_shmcb
RUN sed -i '/SSLCertificateFile.*snakeoil\.pem/c\SSLCertificateFile \/etc\/ssl\/certs\/cert.pem' /etc/apache2/sites-available/default-ssl.conf
RUN sed -i '/SSLCertificateKeyFile.*snakeoil\.key/cSSLCertificateKeyFile \/etc\/ssl\/private\/cert-key.pem' /etc/apache2/sites-available/default-ssl.conf
RUN a2ensite default-ssl

