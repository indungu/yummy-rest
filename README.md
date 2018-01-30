# Yummy REST
[![Build Status](https://travis-ci.org/indungu/yummy-rest.svg?branch=develop)](https://travis-ci.org/indungu/yummy-rest)
[![Coverage Status](https://coveralls.io/repos/github/indungu/yummy-rest/badge.svg?branch=develop)](https://coveralls.io/github/indungu/yummy-rest?branch=develop) [![Maintainability](https://api.codeclimate.com/v1/badges/072ecd4ee97bb2e437d9/maintainability)](https://codeclimate.com/github/indungu/yummy-rest/maintainability)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c5cdd555fe3c4ac7abb40ed49d369882)](https://www.codacy.com/app/indungu/yummy-rest?utm_source=github.com&utm_medium=referral&utm_content=indungu/yummy-rest&utm_campaign=badger)

This is a RESTful API implementation of the Yummy Recipes developer challenge. It is based on Flask with data persistence achieved using PostgreSQL.

## Prerequisites

1. Python version 3.6 or higher
2. virtual environment creator of choice (This example uses `pipenv`)
3. PostgreSQL 9.6

## Install

### Database Setup

```bash
$ cd path/to/your/workspace/
$ createdb -U <superuser_account> yummy_rest_db # replace the angle brackets with name of a user with db create permissions
$ psql -U <superuser_account> yummy_rest_db < "utilities/yummy_rest_db.sql" # this creates the database from .sql dump file
$ psql -U <superuser_account>
<super_user_account>=# \l # This will return a list of your databases. Check to confirm yummy_rest_db is listed
<super_user_account>=# \q # exit psql
```

Each of the above `psql` commands requests you to enter a password for the user provided. This project runs on a database created with the default superuser account `postgres` and a basic password `password`; this will need to be adjusted accodingly on the database URI string:
`APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://<superuser_account>:<password>@localhost:5432/yummy_rest_db`

### Clone source

```bash
$ git clone -b develop https://github.com/indungu/yummy-rest # Clone the repository on the development branch
$ cd yummy-rest
$ pipenv install --three # Install/Create virtual environment
$ pipenv shell # Activate virtual env
$ pip install -r requirements.txt # Install package dependecies
$ python run.py # run the app - or in this case the API
```

## To-Do

Enable users to:

1. Register, login and manage their accounts `/auth/*`
2. Create, update, view and delete a category `/category/*`
3. Add, update, view or delete recipes