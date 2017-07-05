# Firefly

[![Build Status](https://travis-ci.org/rorodata/firefly.svg?branch=master)](https://travis-ci.org/rorodata/firefly)

Function as a service.

# How to install?

Install firefly from source using:

	pip install firefly-python

# How to use?

Create a simple python function.

	# fib.py

	def fib(n):
		if n == 0 or n == 1:
			return 1
		else:
			return fib(n-1) + fib(n-2)

And run it using firefly.

	$ firefly fib.fib
	[2017-06-08 12:45:11 +0530] [20237] [INFO] Starting gunicorn 19.7.1
	[2017-06-08 12:45:11 +0530] [20237] [INFO] Listening at: http://127.0.0.1:8000 (20237)
	...

That started the fib as a service listening at <http://127.0.0.1:8000/>.

The service can be invoked by sending a POST request.

	$ curl -d '{"n": 10}' http://127.0.0.1:8000/
	89

# Documentation

<http://firefly-python.readthedocs.io/>

# Features Planned

* Auto reload
* Token-based authentication
* supporting other input and output content-types in addition to json. (for example, a function to resize an image)
* serverless deployment
