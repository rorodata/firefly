Firefly
=======

.. image:: https://travis-ci.org/rorodata/firefly.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/rorodata/firefly

Function as a service.

How to install?
---------------

Install firefly from source using:

	pip install firefly-python

How to use?
-----------

Create a simple python function.

	# fib.py

	def fib(n):
		if n == 0 or n == 1:
			return 1
		else:
			return fib(n-1) + fib(n-2)

And run it using firefly.

	$ firefly fib.fib
	http://127.0.0.1:8000/
	...

That started the fib function as a service listening at <http://127.0.0.1:8000/>.

Let us see how to use it with a client.

	>>> import firefly
	>>> client = firefly.Client("http://127.0.0.1:8000/")
	>>> client.square(n=4)
	16

The service can also be invoked by sending a POST request.

	$ curl -d '{"n": 10}' http://127.0.0.1:8000/fib
	89

Documentation
-------------

<http://firefly-python.readthedocs.io/>

Features Planned
----------------

- Auto reload
- supporting other input and output content-types in addition to json. (for example, a function to resize an image)
- serverless deployment
