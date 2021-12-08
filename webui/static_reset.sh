if [ -d "static/bootstrap" ]
then
  rm -r static/bootstrap/
fi
unzip static/bootstrap.zip -d static
mv static/bootstrap-5.1.3-dist static/bootstrap

if [ -d "static/fa" ]
then
  rm -r static/fa/
fi
unzip static/fa.zip -d static
mv static/fontawesome-free-5.15.4-web static/fa
