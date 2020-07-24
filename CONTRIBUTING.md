# <img src="layup_list/static/img/logo-sm.png" alt="logo" width=30> Contributing to Layup List

Our <a href="https://github.com/layuplist/layup-list/issues">issues</a> page has some ideas for buxfixes and feature improvements (though you aren't limited to this list).

To contribute code, make a pull request. Github has a great <a href="https://guides.github.com/activities/contributing-to-open-source/">guide</a> for how you can go about doing this.

Feel free to email <a href="mailto:support@layuplist.com">support@layuplist.com</a> if you need any help.

Local Setup (macOS or OS X)
-----------------
#### Installation
* Use Python 2.7.16
* Install [Homebrew](http://brew.sh/), [node.js](https://nodejs.org/en/), and Postgres (we recommend [Postgres.app](http://postgresapp.com/) with their [CLI Tools](http://postgresapp.com/documentation/cli-tools.html)).
* Install the [Heroku CLI](https://cli.heroku.com). You don't need a Heroku account, they just offer good tools for configuration.
* Install Redis using `brew install redis`.
* We use yuglify to compress the static files. Install using `sudo npm install -g yuglify`.
* Install forego using `brew install forego`. This is used to run the server.
* Run `easy_install pip` if you do not have pip.
* Run `pip install virtualenv` if you do not have virtualenv.
* Run `virtualenv venv` to create a Python virtual environment.
* Run `createdb layuplist`.
* [Clone](https://help.github.com/articles/cloning-a-repository/) the main repository. `git clone https://github.com/layuplist/layup-list.git`.
* Create a `.env` file in the root directory of the repository (fill out the items in brackets):

  ```bash
  DATABASE_URL=postgres://[YOUR_USERNAME]@localhost:5432/layuplist
  REDIS_URL=redis://[YOUR_USERNAME]@localhost:6379
  SECRET_KEY=[SOME_LONG_RANDOM_STRING]
  DEBUG=True
  CURRENT_TERM=20X
  OFFERINGS_THRESHOLD_FOR_TERM_UPDATE=100
  ```

* Run `source ./scripts/dev/environment.sh` to set up the heroku development environment.
* Run `source ./scripts/dev/virtualize.sh` to activate the virtual environment.
* Install Python dependencies using `pip install -r requirements.txt`.

Developing
----------

**Note:** Every time you start up a new Terminal window or tab, you need to run both of the below commands. You already ran them above, but if you close your terminal and want to work on this project again later, you must run them again.

```bash
source ./scripts/dev/environment.sh
source ./scripts/dev/virtualize.sh
```

You will also need to have Postgres and Redis running. Do this by opening `Postgres.app` or running `redis-server`.

After you have completed all the steps in **Local Setup**, you can start the development server by running:

```bash
python manage.py collectstatic        # create static files
forego start                          # run the server
```

You may need to run the second command multiple times while developing, mostly if you are working with the front-end. I run this whenever I start the server:
```bash
echo 'yes' | python manage.py collectstatic; forego start;
```

After running `forego start` you can navigate to your browser and visit `http://localhost:5000` to see your local version of Layup List.

Populating Initial Data
-----------------------
Open the Django shell using `python manage.py shell` and run 
```python
from scripts import crawl_and_import_data
crawl_and_import_data()
```

This will crawl the timetable and medians for data to use during development. By default, this does not crawl the ORC, as that takes a long time. If you would like to crawl the ORC, you can run `crawl_and_import_data(include_orc=True)` instead.

Setting Up An Account
---------------------
After successfully running the server, you can create an user account by signing up through the website. You won't receive a confirmation email, so you have the activate the account through the Django shell. Open the Django shell using `python manage.py shell` and run the following code:
```python
from django.contrib.auth.models import User
u = User.objects.last()  # last created user
u.is_active = True
u.save()
```
If you'd like to have access to the admin panel at `/admin`, also run these before `u.save()`:
```python
u.is_staff = True
u.is_admin = True
```

Linting code and Running Tests
------------------------------
We offer two scripts, `./scripts/dev/lint.sh` and `./scripts/dev/test.sh` that you should run occasionally during development. You may need to `pip install pep8`.

Stack
-----
Languages: Python, Javascript (JSX enabled), HTML, CSS

Frameworks and Services: Django, Postgres, Heroku, SendGrid, jQuery, Bootstrap, d3.js, Node.js
