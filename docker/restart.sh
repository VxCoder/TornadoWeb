docker kill $(docker ps -a -q)
docker rm $(docker ps -a -q)
sudo docker-compose up -d
