docker run -it -d --name logger-1 --network test --network-alias logger -v "$(pwd)":/app -w /app 0a6cd0db41a4 sh
