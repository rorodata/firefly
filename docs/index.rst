.. Firefly documentation master file, created by
   sphinx-quickstart on Wed Jun 21 11:32:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

firefly
=======

firefly is a function as a service framework which can be used to deploy
functions as a web service. In turn, the functions can be accessed over a
REST based API or RPC like client. In short, ``firefly`` puts your
**functions on steroids**.

Machine Learning models can even be deployed over ``firefly``.

Installation
------------

``firefly`` can be installed by using ``pip`` as:
::

  $ pip install firefly-python

You can check the installation by using:
::

  $ firefly -h

Basic Usage
-----------

Create a simple python function:
::

  # funcs.py

  def square(n):
    return n**2

And then this function can run through ``firefly`` by the following:
::

  $ firefly funcs.square
  http://127.0.0.1:8000/
  ...

This function is now accessible at ``http://127.0.0.1:8000/square`` .
An inbuilt ``Client`` is also provided to communicate with the ``firefly``
server. Example usage of the client:
::

  >>> from firefly.client import Client
  >>> client = Client("http://127.0.0.1:8000")
  >>> client.square(n=4)
  16

Besides that, you can also use ``curl`` or any software through which you can do
a POST request to the endpoint.
::

  $ curl -d '{"n": 4}' http://127.0.0.1:8000/square
  16

``firefly`` supports for any number of functions. You can pass multiple
functions as:
::

  $ firefly funcs.square funcs.cube

The functions ``square`` and ``cube`` can be accessed at ``127.0.0.1:8000/square``
and ``127.0.0.01:8000/cube`` respectively.

Authentication
--------------

``firefly`` also supports token-based authentication. You will need to pass a token
through the CLI or the config file.
::

  $ # CLI Usage
  $ firefly --token abcd1234 funcs.square
  http://127.0.0.1:8000/


The token now needs to be passed with each request.
::

  >>> from firefly.client import Client
  >>> client = Client("http://127.0.0.1:8000", auth_token="abcd1234")
  >>> client.square(n=4)
  16

If you are using anything other than inbuilt-client, the ``Authorization``
HTTP header needs to be set in the POST request.
::

  $ curl -d '{"n": 4}' -H "Authorization: Token abcd1234" http://127.0.0.1:8000/square
  16

Using a config file
-------------------

``firefly`` can also take a configuration file with the following schema:
::

  # config.yml

  version: 1.0
  token: "abcd1234"
  functions:
    square:
      path: "/square"
      function: "funcs.square"
    cube:
      path: "/cube"
      function: "funcs.cube"
    ...

You can specify the configuration file as:
::

  $ firefly -c config.yml
  http://127.0.0.1:8000/
  ...

Deploying a ML model
--------------------

Machine Learning models can also be deployed by using ``firefly``. You need to
wrap the prediction logic as a function. For example, if you have a directory
as follows:
::

  $ ls
  model.py classifier.pkl

where ``classifier.pkl`` is a ``joblib`` dump of a SVM Classifier model.
::

  # model.py
  from sklearn.externals import joblib

  clf = joblib.load('classifier.pkl')

  def predict(a):
      predicted = clf.predict(a)    # predicted is 1x1 numpy array
      return int(predicted[0])

Invoke ``firefly`` as:
::

  $ firefly model.predict
  http://127.0.0.1:8000/
  ...

Now, you can access this by:
::

  >>> from firefly.client import Client
  >>> client = Client("http://127.0.0.1:8000")
  >>> client.predict(a=[5, 8])
  1

You can use any model provided the function returns a JSON friendly data type.

Firefly with gunicorn
---------------------

``firefly`` applications can also be deployed using `gunicorn <http://gunicorn.org/>`_ .
The arguments that are passed to ``firefly`` via CLI can be set as environment
variables.
::

  $ gunicorn firefly.main.app -e FIREFLY_FUNCTIONS="funcs.square" -e FIREFLY_TOKEN="abcd1234"
  [2017-07-19 14:47:57 +0530] [29601] [INFO] Starting gunicorn 19.7.1
  [2017-07-19 14:47:57 +0530] [29601] [INFO] Listening at: http://127.0.0.1:8000 (29601)
  [2017-07-19 14:47:57 +0530] [29601] [INFO] Using worker: sync
  [2017-07-19 14:47:57 +0530] [29604] [INFO] Booting worker with pid: 29604

If you want to deploy multiple functions, pass them as a comma-seperated list.
::

  $ gunicorn firefly.main.app -e FIREFLY_FUNCTIONS="funcs.square,funcs.cube" -e FIREFLY_TOKEN="abcd1234"

Deployment on Heroku
--------------------

``firefly`` functions are deploying on any cloud platform. This section shows
how you can deploy ML models to `Heroku <http://heroku.com/>`_ . There are two
important files apart from your model code that you will need to have in your
application root directory - ``Procfile`` and ``requirements.txt``. ``Procfile``
lets Heroku know what sort of process you want to run and what command it should
run. ``requirements.txt`` specifies dependencies of your code.
::

  # requirements.txt
  firefly-python
  sklearn
  numpy
  scipy

This ``Procfile`` tells Heroku to run ``firefly`` serving the ``predict``
function inside the ``model`` script.
::

  # Procfile
  web: gunicorn firefly.main:app -e FIREFLY_FUNCTIONS="model.predict"

::

  $ ls
  model.py classifier.pkl requirements.txt Procfile

Now that everything is setup on your machine, we can deploy the application to
Heroku.

::

  $ git add .

  $ git commit -m "Added a Procfile."

  $ heroku login
  Enter your Heroku credentials.
  ...

  $ heroku create
  Creating intense-falls-9163... done, stack is cedar
  http://intense-falls-9163.herokuapp.com/ | git@heroku.com:intense-falls-9163.git
  Git remote heroku added

  $ git push heroku master
  ...
  -----> Python app detected
  ...
  -----> Launching... done, v7
       https://intense-falls-9163.herokuapp.com/ deployed to Heroku

For more information about deploying python applications to Heroku, go
`here <https://devcenter.heroku.com/articles/deploying-python>`_ .
