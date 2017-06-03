# Firefly

Function as a service.

# How to install?

Install firefly from source using:

	pip install git+git://github.com/rorodata/firefly

# How to use?

Create a simple python function.

	# fib.py

	def fib(n):
		if n == 0 or n == 1:
			return 1
		else:
			return fib(n-1) + fib(n-2)

And run it using firefly.

	$ firefly fib:fib

