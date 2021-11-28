# if this is not an arm machine
if [ "$(uname -m)" != "armv8l" ] &&  "$(uname -m)" != "armv8l" ]; then
    echo "This is not an ARM machine"
fi

# apt-get update && apt-get install -y unixodbc unixodbc-dev
# pip install pyodbc
# sudo apt-get install freetds-dev freetds-bin tdsodbc
# sudo odbcinst -i -d -f /usr/share/tdsodbc/odbcinst.ini



# loop until docker daemon is started for max of 30 seconds
i=0
while [ ! -S /var/run/docker.sock ] && [ $i -lt 30 ]
do
    echo "Waiting for docker daemon to be available..."
    i+=1
    sleep 1
done

echo "starting build"
docker build -t webui /code/
docker run -d -v /code/webui/sqlite:/code/webui/sqlite -v /code/webui/media:/code/webui/media -e THISURL=$THISURL -e BUILDNUMBER=$BUILDNUMBER -p 80:80 webui
echo "container running"

cd /code/api
flask run -h 0.0.0.0