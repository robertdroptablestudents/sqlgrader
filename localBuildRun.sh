docker container stop sqlgrader
docker container rm sqlgrader
docker build --build-arg BUILDID="mylocalbuild" -t sqlgrader .
docker run -p 80:80 --privileged --name sqlgrader -d sqlgrader