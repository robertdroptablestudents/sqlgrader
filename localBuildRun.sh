docker container stop sqlgrader
docker container rm sqlgrader
docker build --build-arg BUILDID="localbuild" -t sqlgrader .
docker run -p 80:80 --privileged --name sqlgrader -e DJANGO_SUPERUSER_PASSWORD=abcde12345 -d sqlgrader
