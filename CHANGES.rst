Firefly changelog
=================

Version 0.1.7 - 2017-09-16
--------------------------

* Added a hack to allow extending firefly
* Made it possible to inject new headers when sending a request by extending the Client
* Better error reporting in the client when the server is not running

Version 0.1.6 - 2017-09-14
--------------------------

* Added support for logging
* Fixed the issue of client not using the path specified in the function specs

Version 0.1.5 - 2017-08-23
--------------------------

* Added support for returning a file object from a function
* Added support for specifying config file as environment variable
* Better error reporting

Version 0.1.4 - 2017-07-25
--------------------------

* Bug fixes

Version 0.1.3 - 2017-07-25
--------------------------

* Fixed the issue with the client when the URL has training / character
* Added support for docstrings in the client functions
* Added support for sending files to the firefly app using multipart/form-data content-type

Version 0.1.2 - 2017-07-19
--------------------------

* Switched to using wsgiref as the default server instead of gunicorn for better portability
* Updated documentation to show how to deploy using gunicorn and on Heroku
* Better error reporting

Version 0.1.1 - 2017-07-10
--------------------------

* Added support for token-based authentication

Version 0.1.0 - 2017-06-30
--------------------------

* First public release
