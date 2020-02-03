python-jose-cryptodome
===========

A JOSE implementation in Python using pycryptodome instead pycrypto.
Stop using pycrypto use pycryptodome_.

|Build Status| |Coverage Status| |Docs|

Docs are available on ReadTheDocs_.

The JavaScript Object Signing and Encryption (JOSE) technologies - JSON
Web Signature (JWS), JSON Web Encryption (JWE), JSON Web Key (JWK), and
JSON Web Algorithms (JWA) - collectively can be used to encrypt and/or
sign content using a variety of algorithms. While the full set of
permutations is extremely large, and might be daunting to some, it is
expected that most applications will only use a small set of algorithms
to meet their needs.


Principles
----------

This is a JOSE implementation that is not compatible with Google App Engine
as it uses pycryptodome.


Installation
------------

::

    $ pip install python-jose-cryptodome

Usage
-----

.. code-block:: python

    >>> from jose import jwt
    >>> token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
    u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJ2YWx1ZSJ9.FG-8UppwHaFp1LgRYQQeS6EDQF7_6-bMFegNucHjmWg'

    >>> jwt.decode(token, 'secret', algorithms=['HS256'])
    {u'key': u'value'}


Thanks
------

This library was originally based heavily on the work of the folks over at PyJWT_.

.. |Build Status| image:: https://travis-ci.org/capless/python-jose-cryptodome.svg?branch=master
   :target: https://travis-ci.org/capless/python-jose-cryptodome
.. |Coverage Status| image:: http://codecov.io/github/capless/python-jose-cryptodome/coverage.svg?branch=master
   :target: http://codecov.io/github/capless/python-jose-cryptodome?branch=master
.. |Docs| image:: https://readthedocs.org/projects/python-jose/badge/
   :target: https://python-jose.readthedocs.org/en/latest/
.. _ReadTheDocs: https://python-jose.readthedocs.org/en/latest/
.. _PyJWT: https://github.com/jpadilla/pyjwt
.. _pycryptodome: https://blog.sqreen.io/stop-using-pycrypto-use-pycryptodome/



