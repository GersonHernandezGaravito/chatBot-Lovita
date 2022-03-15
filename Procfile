heroku ps:scale web=1
heroku buildpacks:clearheroku buildpacks:add --index heroku/python

web: python /app.py runserver 0.0.0.0:5000