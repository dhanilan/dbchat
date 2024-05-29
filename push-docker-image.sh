docker build . -t $DOCKER_USERNAME/dbchat:latest
docker login
docker push $DOCKER_USERNAME/dbchat:latest