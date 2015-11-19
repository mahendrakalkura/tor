# Requirements

- Python 2.7.X - https://www.python.org
    - virtualenvwrapper - http://virtualenvwrapper.readthedocs.org/en/latest/index.html
- Tor: https://www.torproject.org/
- Polipo: http://www.pps.univ-paris-diderot.fr/~jch/software/polipo/

# How to install?

```
$ mkdir tor
$ cd tor
$ git clone --recursive git@github.com:mahendrakalkura/tor.git .
$ cp settings.py.sample settings.py
$ mkvirtualenv tor
$ pip install -r requirements.txt
```

# How to start?

```
$ cd tor
$ workon tor
$ python 1.py tor
$ python 1.py polipo
$ python 1.py report
```

# How to stop?

```
$ cd tor
$ workon tor
$ python 1.py reset
```
