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

  $ pip install git+git://github.com/rorodata/firefly

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
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Starting gunicorn 19.7.1
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Listening at: http://127.0.0.1:8000
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

The functions ``square`` and ``cube`` can be accessed at ``127.0.0.1:8000/sqaure``
and ``127.0.0.01:8000/cube`` respectively.

Using a config file
-------------------

``firefly`` can also take a configuration file with the following schema:
::

  # config.yml

  version: 1.0
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
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Starting gunicorn 19.7.1
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Listening at: http://127.0.0.1:8000
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

  clf = joblib.load('clf_dump.pkl')

  def predict(a):
      predicted = clf.predict(a)    # predict is 1x1 numpy array
      return int(predicted[0])

Invoke ``firefly`` as:
::

  $ firefly model.predict
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Starting gunicorn 19.7.1
  [2017-06-21 15:42:16 +0530] [31482] [INFO] Listening at: http://127.0.0.1:8000
  ...

Now, you can access this by:
::

  >>> from firefly.client import Client
  >>> client = Client("http://127.0.0.1:8000")
  >>> client.predict(a=[5, 8])
  1

You can use any model provided the function returns a JSON friendly data type.
