# Requirements
Make sure you machine supports Docker, Docker-compose (3.9)

# Clone project
```
git clone git@github.com:detiuaveiro/assignment-1---vulnerable-ehealth-application-grupo_19.git
```


# Build and run
This projects uses docker compose, before build and running we should make sure that the container have permissions into the files, the following commands transfers ownsership of src folder from you to www-data user (docker container user)
```
cd app
sudo chown -R www-data:www-data src
```

After that, in order to build the container run the following command
```
sudo docker-compose up --build
```

The website will be visible at `localhost:9005` and phpmyadming interface at `localhost:9006`.

Lastly access the following url `localhost:9005/reset.php` in order to populate and initialize database with example data (this step is crucial).