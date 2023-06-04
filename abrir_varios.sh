docker run -it -d --name entry-1 --network test --network-alias entry -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name entry-2 --network test --network-alias entry -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name entry-3 --network test --network-alias entry -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name entry-4 --network test --network-alias entry -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name entry-5 --network test --network-alias entry -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-1 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-2 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-3 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-4 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-5 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --name logger-6 --network test --network-alias logger -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --network test -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --network test -v "$(pwd)":/app -w /app peewee sh ;
docker run -it -d --network test -v "$(pwd)":/app -w /app peewee sh
