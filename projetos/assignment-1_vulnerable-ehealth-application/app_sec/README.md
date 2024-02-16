# Requirements

Make sure you machine supports Docker, Docker-compose (3.9)

# Clone project

```
git clone git@github.com:detiuaveiro/assignment-1---vulnerable-ehealth-application-grupo_19.git
```

# Build and run

This projects uses docker compose, before build and running we should make sure that the container have permissions into the files, the following commands transfers ownsership of src folder from you to www-data user (docker container user)

```
cd app_sec
sudo chown -R www-data:www-data src
```

After that, in order to build the container run the following command

```
sudo docker-compose up --build
```

The website will be visible at `localhost:9008` and phpmyadming interface at `localhost:9009`.

Lastly access the following url `localhost:9008/reset.php` in order to populate and initialize database with example data (this step is crucial).

# Version with certificates and https

In order for the application to have secure traffic and encripted connection between the client and server, especially when credentials are being exchanged and the user is logging into his account, a local certificate was issued. However, we didn't include a root certificate, because that would have to be imported by you and isn't needed in this instance.

The website with https can be acessed at `localhost:9443` (it's just a different port for secure traffic to go through).

The first time that the website is accessed, your browser will probably warn you that the website is not secure, that is because it couldn't validate our locally issued encryption certificate. This situation won't affect our encryted data demonstration, so please choose the option to continue to visit the website.