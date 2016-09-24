# <img src="layup_list/static/img/logo-sm.png" alt="logo" width=30> Contributing to Layup List

Our <a href="https://github.com/layuplist/layup-list/issues">issues</a> page has some ideas for buxfixes and feature improvements (though you aren't limited to this list).

To contribute code, simply make a pull request. Github has a great <a href="https://guides.github.com/activities/contributing-to-open-source/">guide</a> for how you can go about doing this.

Contributors will be added to the <a href="https://github.com/layuplist">layuplist organization</a>, so you can display your membership on your profile.

Feel free to email <a href="mailto:support@layuplist.com">support@layuplist.com</a> if you need any help.

Local Setup (OSX)
-----------------

* [Clone](https://help.github.com/articles/cloning-a-repository/) the repository
* Install [Homebrew](http://brew.sh/)
* Install Postgres. We recommend [Postgres.app](http://postgresapp.com/). If you do this, be sure to set up the [CLI Tools](http://postgresapp.com/documentation/cli-tools.html). Open the application
* Install the [Heroku CLI](https://cli.heroku.com). You don't need a Heroku account, they just offer good tools for configuration
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
  CURRENT_TERM=16S
  ```
* Run `source ./scripts/dev/environment.sh` to set up the development environment
* Install Python dependencies using `pip install -r requirements.txt`
* Run `bash ./scripts/dev/import_initial_data.sh` to populate the database

Contact support@layuplist.com if you need help.

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

Stack
-----

Languages: Python, Javascript (JSX enabled), HTML, CSS

Frameworks and Services: Django, Postgres, Heroku, SendGrid, jQuery, Bootstrap, d3.js, PhantomJS, Node.js, React
