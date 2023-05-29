docker run -it \
--network test \
--network-alias entry \
-v "$(pwd)":/app \
-w /app \
ff7 \
sh