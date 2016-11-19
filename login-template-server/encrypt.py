import Crypto.Random
from Crypto.Protocol import KDF
from google.appengine.ext import ndb
from datetime import datetime

#Attribution: BRIAN M HUNT
#See https://brianmhunt.github.io/articles/strong-crypto-python-passwords/

class Credentials(ndb.Model):
    """Credentials to authenticate a person.
    """
    _randf = None
    ITERATIONS_2015 = 60000 #Should be 100000 but it's somewhat slow 
    ITER_OFFSET = -257
    DK_LEN = 32
    dk = ndb.BlobProperty(indexed=False)
    salt = ndb.BlobProperty(indexed=False)
    iterations = ndb.IntegerProperty(indexed=False)
    # Not used currently
    failed_attempts = ndb.IntegerProperty(indexed=False)
    computers_authorized = ndb.JsonProperty()
    other_factor = ndb.StringProperty(indexed=False)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "<Credentials: {}>".format(dict(
            failed_attempts=self.failed_attempts
        ))

    @property
    def random_stream(self):
        if not self._randf:
            self._randf = Crypto.Random.new()
        return self._randf

    def _multiplier(self):
        """The multiplier to increase the KDF over time.

        The integer returned doubles every two years from 2015.
        """
        start = datetime(2015, 1, 1)
        now = datetime.now()
        return 2 ** ((now - start).days / 730.0)

    def _iterations(self):
        """The number of iterations for this KDF
        """
        base_iters = int(self.ITERATIONS_2015 * self._multiplier())
        entropy = int(
            self.random_stream.read(2).encode('hex'), 16
        ) % int(base_iters * 0.06)
        return base_iters + entropy

    def generate_dk(self, token):
        """Generate a defined key for a given token in hex
        """
        return KDF.PBKDF2(token, self.salt, dkLen=self.DK_LEN,
                          count=self.iterations + self.ITER_OFFSET
                          ).encode('hex')

    def set_dk(self, token):
        """Set the derived key from the given token, generating iterations
        and salt as necessary.
        """
        self.iterations = self._iterations()
        self.salt = self.random_stream.read(32).encode('hex')
        self.dk = self.generate_dk(token)

    def verify(self, token):
        """Determine if the given token matches the saved token
        """
        if not self.dk:
            return
        return self.dk == self.generate_dk(token)

