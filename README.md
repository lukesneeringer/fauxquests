## Welcome to fauxquests

[![Build Status](https://travis-ci.org/lukesneeringer/fauxquests.png?branch=master)](https://travis-ci.org/lukesneeringer/fauxquests) [![Coverage](https://coveralls.io/repos/lukesneeringer/fauxquests/badge.png?branch=master)](https://coveralls.io/r/lukesneeringer/fauxquests)

The purpose of **fauxquests** is to make it easy to mock HTTP requests
in your unit tests without hitting the outside world.

#### Installing fauxquests

Install fauxquests using pip: `pip install fauxquests`.

fauxquests runs on Python 2.7 and Python 3.3. (It probably also works fine
on Python 2.6, but it's not explicitly tested against it.)

If you're using fauxquests with Python 2.7, you'll also need to install
`mock` using pip; if you're on Python 3.3, fauxquests will use the version
in the standard library.

#### Using fauxquests

fauxquests contains a class called `FauxServer`, and instances of the
`FauxServer` class can be used as a context manager.

Within the context manager, you can register endpoints and the responses
you expect back:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()
with faux_server as fs:
    fs.register('http://foo/', 'My awesome response.')

    r = requests.get('http://foo/')
    r.content  # My awesome response.
```

The FauxServer also rejects any URLs it doesn't have registered, which
prevents you from calling the outside world in your unit tests unintentionally:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()

r = requests.get('http://www.google.com/')      # Downloads from google.com
with faux_server as fs:
    r = requests.get('http://www.google.com/')  # Exception: UnregisteredURL
```

The registration of a URL and response only lasts for the duration of
the context manager. However, for reusability, you can also register
a response on the FauxServer instance, and it will be preserved across
multiple context manager uses:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()
faux_server.register('http://bar/', 'My MORE awesome response.')
with faux_server as fs:
    fs.register('http://foo/', 'My awesome response.')

    requests.get('http://bar/').content   # My MORE awesome response.
    requests.get('http://foo/').content   # My awesome response.

with faux_server as fs:
    requests.get('http://bar/').content   # My MORE awesome response.
    requests.get('http://foo/').content   # Exception: UnregisteredURL
```

#### Mocking JSON Responses

If you're mocking an API that sends back JSON data, you can more easily
mock your responses using the `register_json` method:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()
with faux_server as fs:
    fs.register_json('http://foo/', { 'spam': True })

    r = requests.get('http://foo/')
    r.json()   # { 'spam': True }
```

#### Query Strings in URLs

fauxquests has special handling for query-strings in URLs, in two ways.
First, if fauxquests receives a request for a URL that contains the exact
URL you registered but a _superset_ of your query string, it will send
the appropriate response anyway:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()
faux_server.register_json('http://api/?q=kitties', { 'results': [] })

with faux_server as fs:
    r = requests.get('http://api/?api_key=01234567&q=kitties')
    r.json()  # { 'results': [] }
```

Second, you can (optionally) specify query string pieces as keyword
arguments in the `register` and `register_json` method:

```python
import fauxquests
import requests

faux_server = fauxquests.FauxServer()
faux_server.register_json('http://foo/', 'My response!', bar=1)

with faux_server as fs:
    requests.get('http://foo/?bar=1').content  # My response!
```

#### URL Patterns

Lastly, fauxquests allows you to provide a URL pattern to `FauxServer`,
for situations where you are mocking lots of requests to the same server,
and want to focus on what is different:

```python
import fauxquests

faux_server = FauxServer(url_pattern='https://api.twitter.com/1.1/%s.json')
faux_server.register_json('statuses/user_timeline', { ... })
faux_server.register_json('statuses/home_timeline', { ... })
faux_server.register_json('search/tweets', { ... })
```

The `url_pattern` argument should include one `%s` placeholder, and the
URL fragments you register will be used in its place.

#### License & Credits

  * fauxquests is New BSD licensed.
  * A special thanks to Łukasz Langa, author of [requests-testadapter][1],
    which was a springboard for this project.

[1]: https://github.com/ambv/requests-testadapter
