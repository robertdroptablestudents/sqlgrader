docker container stop sqlgrader
docker container rm sqlgrader
docker build --build-arg BUILDID="localbuild" -t sqlgrader .
docker run -p 80:80 --privileged --name sqlgrader -e DJANGO_SUPERUSER_PASSWORD=abcde12345 -d sqlgrader


# look for -l flag to see if you want to see the logs
while getopts l flag
do
    case "${flag}" in
        l)
            ${containerselector}
            ;;
    esac
done

# if ${containerselector} is webui, docker exec
if [$containerselector == "webui"]
then
    docker exec -it sqlgrader bash
    docker logs -f webui
elif [$containerselector == "sqlgrader"]
then
    docker logs -f sqlgrader
fi
