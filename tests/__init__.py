from urllib2 import urlopen, HTTPError, URLError

from tuttle.addons.netutils import hostname_resolves


def is_online():
        try:
            # If google is available, it mean Internet is up
            response = urlopen("http://www.google.com")
            some_data = response.read(0)
        except (HTTPError, URLError) as e:
            return False
        return True


online = is_online()


bad_resolving = hostname_resolves("this-host-does-not-exists")