install requiments.txt

First you need to create a postgres databasae with name ecommerce 

then create a table, add fake data or delete data which i addend in app/db_scripts

then after loading data u run the backend and frontned

also add .env file and put 
OPENAI_API_KEY, DATABASE_URL


#################################################33333
If using git codebase

then fisrt check the docker-compose file in root folder 

run docker-compose file - docker-compose up -d

to run the db on terminal then first install package for psql then - psql -h localhost -U postgres -d ecommerce 
put your db password 

then run the script for crete_table and add fake_add

then run backend and frontend
