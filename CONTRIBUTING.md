# <img src="https://raw.githubusercontent.com/layuplist/layup-list/master/layup_list/static/img/logo-sm.png" width=30> Contributing to Layup List

Layup List has been built to be easy to contribute to, especially for learning developers. 

Please don't hesitate to reach out if you would like to contribute or need help doing so. Emailing <a href="mailto:support@layuplist.com">support@layuplist.com</a> is fine.

This guide will go over:

* What Layup List is built on 
* How to set up Layup List locally
* How to contribute to Layup List
* The benefits of contributing

Stack
-----

You DO NOT have to know all of these to contribute to Layup List. Many of them are used in only a small portion of the codebase, and most features will only require working with one or two of the technologies.

Languages used: Python, Javascript (JSX enabled), HTML, CSS

Frameworks and Services:
* *Django*: Python MVC web application framework used for the backend
* *Postgres*: Relational database -- interactions are handled through Django's ORM
* *Heroku*: Platform for deployment, everything in the `bin` folder is related, Procfile too
* *SendGrid*: Email delivery service
* *jQuery*: Javascript framework used for asynchronous requests (such as retrieving the median chart data)
* *Bootstrap*: Front-end framework for styling
* *d3.js*: Javascript library used for charting
* *PhantomJS*: Used for the web crawlers (including ORC, medians, and timetable)
* *Node.js*: Used for Course Picker parsers (with cheerio), yuglify
* *React*: Javascript library used experimentally and dropped. LL is set up to use it though, so you may use it if you'd like

Local Setup
-----------

There are other ways to set it up, for sure, and you may not end up needing all of the dependencies and steps. However, if you set it up this way you shouldn't run into any configuration issues. Specific commands may be OSX dependendent, however the general idea is the same for other systems.

* [Clone](https://help.github.com/articles/cloning-a-repository/) the repository
* Install [Homebrew](http://brew.sh/)
* Install Postgres. We recommend [Postgres.app](http://postgresapp.com/). If you do this, be sure to set up the [CLI Tools](http://postgresapp.com/documentation/cli-tools.html). Open the application
* Install the [Heroku Toolbelt](https://toolbelt.heroku.com/). You don't need a Heroku account, they just offer good tools for configuration
* We use yuglify to compress the static files. Install using `sudo npm install -g yuglify`. If this doesn't work, you may need to install [node.js](https://nodejs.org/en/).
* Install forego using `brew install forego`
* Run `sudo easy_install pip` if you do not have pip
* Run `sudo pip install virtualenv` if you do not have virtualenv
* Run `virtualenv venv --no-site-packages` to create a Python virtual environment
* Create the Layup List database. Run `psql` and then type `CREATE DATABASE layuplist;`
* Create a `.env` file in the root directory of the repository (fill out the items in brackets):

  ```bash
  DATABASE_URL=postgres://[YOUR_USERNAME]@localhost:5432/layuplist
  SECRET_KEY=[SOME_LONG_RANDOM_STRING]
  DEBUG=True
  ```
* Run `source ./scripts/dev/environment.sh` to set up the development environment
* Install Python dependencies using `pip install -r requirements.txt`
* Run `bash ./scripts/dev/setup_data.sh` to initialize the data subfolder
* Run `bash ./scripts/dev/import_initial_data.sh` to populate the database

Contact support@layuplist.com if you need help. The only configuration missing from these instructions is for SendGrid, which involves adding more variables to the `.env` file. Most features won't require this, however.

Running Web Server
------------------

After you have completed all the steps in **Local Setup**, you can start the development server by running:

```bash
source ./scripts/dev/environment.sh   # set up the development environment, if you haven't already
python manage.py collectstatic        # create static files
forego start                          # run the server
```

You may need to run the second command multiple times while developing, mostly if you are working with the front-end. I run this whenever I start the server: 
```bash
echo 'yes' | python manage.py collectstatic; forego start;
```

After running `forego start` you can navigate to your browser and visit `http://localhost:5000` to see your local version of Layup List.

Setting Up An Account
---------------------

After successfully running the server, you can create an user account by signing up through the website. You won't receive a confirmation email, so you have the activate the account through the Django shell. Open the Django shell using `python manage.py shell` and run the following code:

```python
from django.contrib.auth.models import User
u = User.objects.all()[1:][0]  # last created user
u.is_active = True
u.save()
```

If you'd like to have access to the admin panel at `/admin`, also run these before `u.save()`:

```python
u.is_staff = True
u.is_admin = True
```

Running Tests
-------------

To run tests:
```python
python ./manage.py test
```

Create new tests in the `web/tests` folder.

Contributing
------------

Please take a look at our <a href="https://github.com/layuplist/layup-list/issues">issues</a> page for some ideas for features that you can tackle.

To contribute code, simply make a pull request, and we will take a look. Github has a great <a href="https://guides.github.com/activities/contributing-to-open-source/">guide</a> for how you can go about doing this.

Benefits of Contributing
------------------------

In addition to boosting your Github resume, upon contributing we will add you to the <a href="https://github.com/layuplist">layuplist organization</a>, so you can display your membership on your profile. 

If you continue to contribute, you may become a core contributor (e.g. able to push and create branches directly on the repo), get Heroku/SendGrid/admin/email access, etc. 
