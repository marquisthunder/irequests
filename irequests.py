#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
irequests - grequests with context and error handling.
======================================================

 * context over request to response
 * directly send requests and iterate responses
 * `sorted()` style `get`
 * error handling


Usage
-----

Setup and create `iterable` objects::
    >>> import irequests

    >>> items = [
    ...     'url': 'http://www.heroku.com', 'message': 'your custom object #1'},
    ...     'url': 'http://tablib.org', 'message': 'your custom object #2'},
    ...     'url': 'http://httpbin.org', 'message': 'your custom object #3'},
    ...     'url': 'http://python-requests.org', 'message': 'your custom object #4'},
    ...     'url': 'http://kennethreitz.com' 'message': 'your custom object #5'},
    ...      ]

And request then you'll get like below (response order is indefinite)::

    >>> for response in irequests.get(items, key=lambda o: o['url']):
    ...     print(response.context['message'])
    your custom object #1
    your custom object #2
    your custom object #3
    your custom object #4
    your custom object #5


Installation
------------

Wait a moment...

"""
import logging; logger = logging.getLogger(__name__)
import math
import http.client
import requests.hooks
import grequests

__all__ = (
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request',
    )
__version__ = '1.0.0'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
#__url__ = 'http://pypi.python.org/pypi/*'
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
__classifiers__ = [i.strip() for i in '''\
    Environment :: Web Environment
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    Operating System :: OS Independent
    Programming Language :: Python
    Topic :: Internet :: WWW/HTTP :: Dynamic Content
    Topic :: Software Development :: Libraries :: Python Modules
    '''.splitlines() if i.strip()]
__install_requires__ = ['gevent', 'requests', 'grequests']


def request(method, iterable, key=None, ignore_errors=True, **kwargs):
    """Convinient http request iterator.
    Returns a generator of :class:`requests.Response <requests.Response>`.
    See ``requests.request`` and ``grequests``.

    :param iterable: Iterable of URL or context object with ``key`` argument.
                     The item can access by ``response.context``.
    :param key: (optional) URL getter function like ``key`` argument of
                ``list.sort``.
    :param ignore_errors: (optional) If ``True``, ignore non 20x code and
                          transport errors.
    """
    # https://github.com/kennethreitz/requests
    # https://github.com/kennethreitz/grequests
    assert 'return_response' not in kwargs, 'not supported'
    kwargs.setdefault('prefetch', True)
    size = kwargs.pop('size', 2)
    hooks = kwargs.pop('hooks', {})

    def gen_hook_response(item):
        def result(response):
            response.context = item
            if 'response' in hooks:
                return hooks['response'](response)
        return result

    reqs = (grequests.request(
        method,
        key(item) if key else item,
        hooks=dict((i for i in hooks.items() if i[0] in requests.hooks.HOOKS),
                   response=gen_hook_response(item)),
        **kwargs) for item in iterable)

    for response in grequests.imap(reqs, kwargs['prefetch'], size):
        # can't get socket.timeout, requests.packages.urllib3.exceptions.TimeoutError here

        # response.status_code == None if not connectable for some reasons
        if ignore_errors \
           and (not response.status_code \
                or math.floor(response.status_code / 100) != 2):
            logger.error('%s %s', response.url, response.status_code)
            response = requests.hooks.dispatch_hook('error', hooks, response)
            continue

        # read and decode response body
        if kwargs['prefetch']:
            try:
                response.content
            except http.client.HTTPException as e: # e.g. IncompleteRead
                logger.exception('%s', response.url)
                response.error = e
                if ignore_errors:
                    response = requests.hooks.dispatch_hook(
                        'error', hooks, response)
                    continue
            except Exception as e:
                logger.exception('%s', response.url)
                continue

        yield response

    #TODO: call hooks['error'] with not yielded items


get = lambda *a, **k: request('get', *a, **k)
options = lambda *a, **k: request('options', *a, **k)
head = lambda *a, **k: request('head', *a, **k)
post = lambda *a, **k: request('post', *a, **k)
put = lambda *a, **k: request('put', *a, **k)
patch = lambda *a, **k: request('patch', *a, **k)
delete = lambda *a, **k: request('delete', *a, **k)


