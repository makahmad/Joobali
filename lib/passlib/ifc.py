"""passlib.ifc - abstract interfaces used by Passlib"""
#=============================================================================
# imports
#=============================================================================
# core
import logging; log = logging.getLogger(__name__)
import sys
# site
# pkg
from passlib.utils.compat import unicode
from passlib.utils import deprecated_method
# local
__all__ = [
    "PasswordHash",
]

#=============================================================================
# 2/3 compatibility helpers
#=============================================================================
def recreate_with_metaclass(meta):
    """class decorator that re-creates class using metaclass"""
    def builder(cls):
        if meta is type(cls):
            return cls
        return meta(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return builder

#=============================================================================
# PasswordHash interface
#=============================================================================
from abc import ABCMeta, abstractmethod, abstractproperty

# TODO: make this actually use abstractproperty(),
#       now that we dropped py25, 'abc' is always available.

# XXX: rename to PasswordHasher?

@recreate_with_metaclass(ABCMeta)
class PasswordHash(object):
    """This class describes an abstract interface which all password hashes
    in Passlib adhere to. Under Python 2.6 and up, this is an actual
    Abstract Base Class built using the :mod:`!abc` module.

    See the Passlib docs for full documentation.
    """
    #===================================================================
    # class attributes
    #===================================================================

    #---------------------------------------------------------------
    # general information
    #---------------------------------------------------------------
    ##name
    ##setting_kwds
    ##context_kwds

    #: flag which indicates this hasher matches a "disabled" hash
    #: (e.g. unix_disabled, or django_disabled); and doesn't actually
    #: depend on the provided password.
    is_disabled = False

    #: if not None, should be an integer, indicating hash
    #: will truncate any secrets larger than this value.
    truncate_size = None

    #---------------------------------------------------------------
    # salt information -- if 'salt' in setting_kwds
    #---------------------------------------------------------------
    ##min_salt_size
    ##max_salt_size
    ##default_salt_size
    ##salt_chars
    ##default_salt_chars

    #---------------------------------------------------------------
    # rounds information -- if 'rounds' in setting_kwds
    #---------------------------------------------------------------
    ##min_rounds
    ##max_rounds
    ##default_rounds
    ##rounds_cost

    #---------------------------------------------------------------
    # encoding info -- if 'encoding' in context_kwds
    #---------------------------------------------------------------
    ##default_encoding

    #===================================================================
    # primary methods
    #===================================================================
    @classmethod
    @abstractmethod
    def hash(cls, secret,  # *
             **setting_and_context_kwds):  # pragma: no cover -- abstract method
        """
        Hash secret, returning result.
        Should handle generating salt, etc, and should return string
        containing identifier, salt & other configuration, as well as digest.

        :param \*\*settings_kwds:

            Pass in settings to customize configuration of resulting hash.

            .. deprecated:: 1.7

                Starting with Passlib 1.7, callers should no longer pass settings keywords
                (e.g. ``rounds`` or ``salt`` directly to :meth:`!hash`); should use
                ``.using(**settings).hash(secret)`` construction instead.

                Support will be removed in Passlib 2.0.

        :param \*\*context_kwds:

            Specific algorithms may require context-specific information (such as the user login).
        """
        # FIXME:  need stub for classes that define .encrypt() instead ...
        #         this should call .encrypt(), and check for recursion back to here.
        raise NotImplementedError("must be implemented by subclass")

    @deprecated_method(deprecated="1.7", removed="2.0", replacement=".hash()")
    @classmethod
    def encrypt(cls, *args, **kwds):
        """
        Legacy alias for :meth:`hash`.

        .. deprecated:: 1.7
            This method was renamed to :meth:`!hash` in version 1.7.
            This alias will be removed in version 2.0, and should only
            be used for compatibility with Passlib 1.3 - 1.6.
        """
        return cls.hash(*args, **kwds)

    # XXX: could provide default implementation which hands value to
    #      hash(), and then does constant-time comparision on the result
    #      (after making both are same string type)
    @classmethod
    @abstractmethod
    def verify(cls, secret, hash, **context_kwds): # pragma: no cover -- abstract method
        """verify secret against hash, returns True/False"""
        raise NotImplementedError("must be implemented by subclass")

    #===================================================================
    # configuration
    #===================================================================
    @classmethod
    @abstractmethod
    def using(cls, relaxed=False, **kwds):
        """
        Return another hasher object (typically a subclass of the current one),
        which integrates the configuration options specified by ``kwds``.
        This should *always* return a new object, even if no configuration options are changed.

        .. todo::

            document which options are accepted.

        :returns:
            typically returns a subclass for most hasher implementations.

        .. todo::

            add this method to main documentation.
        """
        raise NotImplementedError("must be implemented by subclass")

    #===================================================================
    # migration
    #===================================================================
    @classmethod
    def needs_update(cls, hash, secret=None):
        """
        check if hash's configuration is outside desired bounds,
        or contains some other internal option which requires
        updating the password hash.

        :param hash:
            hash string to examine

        :param secret:
            optional secret known to have verified against the provided hash.
            (this is used by some hashes to detect legacy algorithm mistakes).

        :return:
            whether secret needs re-hashing.

        .. versionadded:: 1.7
        """
        # by default, always report that we don't need update
        return False

    #===================================================================
    # additional methods
    #===================================================================
    @classmethod
    @abstractmethod
    def identify(cls, hash): # pragma: no cover -- abstract method
        """check if hash belongs to this scheme, returns True/False"""
        raise NotImplementedError("must be implemented by subclass")

    @deprecated_method(deprecated="1.7", removed="2.0")
    @classmethod
    def genconfig(cls, **setting_kwds): # pragma: no cover -- abstract method
        """
        compile settings into a configuration string for genhash()

        .. deprecated:: 1.7

            As of 1.7, this method is deprecated, and slated for complete removal in Passlib 2.0.

            For all known real-world uses, hashing a constant string
            should provide equivalent functionality.

            This deprecation may be reversed if a use-case presents itself in the mean time.
        """
        # NOTE: this fallback runs full hash alg, w/ whatever cost param is passed along.
        #       implementations (esp ones w/ variable cost) will want to subclass this
        #       with a constant-time implementation that just renders a config string.
        if cls.context_kwds:
            raise NotImplementedError("must be implemented by subclass")
        return cls.using(**setting_kwds).hash("")

    @deprecated_method(deprecated="1.7", removed="2.0")
    @classmethod
    def genhash(cls, secret, config, **context):
        """
        generated hash for secret, using settings from config/hash string

        .. deprecated:: 1.7

            As of 1.7, this method is deprecated, and slated for complete removal in Passlib 2.0.

            This deprecation may be reversed if a use-case presents itself in the mean time.
        """
        # XXX: if hashes reliably offered a .parse() method, could make a fallback for this.
        raise NotImplementedError("must be implemented by subclass")

    #===================================================================
    # undocumented methods / attributes
    #===================================================================
    # the following entry points are used internally by passlib,
    # and aren't documented as part of the exposed interface.
    # they are subject to change between releases,
    # but are documented here so there's a list of them *somewhere*.

    #---------------------------------------------------------------
    # checksum information - defined for many hashes
    #---------------------------------------------------------------
    ## checksum_chars
    ## checksum_size

    #---------------------------------------------------------------
    # experimental methods
    #---------------------------------------------------------------

    ##@classmethod
    ##def normhash(cls, hash):
    ##    """helper to clean up non-canonic instances of hash.
    ##    currently only provided by bcrypt() to fix an historical passlib issue.
    ##    """

    # experimental helper to parse hash into components.
    ##@classmethod
    ##def parsehash(cls, hash, checksum=True, sanitize=False):
    ##    """helper to parse hash into components, returns dict"""

    # experiment helper to estimate bitsize of different hashes,
    # implement for GenericHandler, but may be currently be off for some hashes.
    # want to expand this into a way to programmatically compare
    # "strengths" of different hashes and hash algorithms.
    # still needs to have some factor for estimate relative cost per round,
    # ala in the style of the scrypt whitepaper.
    ##@classmethod
    ##def bitsize(cls, **kwds):
    ##    """returns dict mapping component -> bits contributed.
    ##    components currently include checksum, salt, rounds.
    ##    """

    #===================================================================
    # eoc
    #===================================================================

class DisabledHash(PasswordHash):
    """
    extended disabled-hash methods; only need be present if .disabled = True
    """

    is_disabled = True

    @classmethod
    def disable(cls, hash=None):
        """
        return string representing a 'disabled' hash;
        optionally including previously enabled hash
        (this is up to the individual scheme).
        """
        # default behavior: ignore original hash, return standalone marker
        return cls.hash("")

    @classmethod
    def enable(cls, hash):
        """
        given a disabled-hash string,
        extract previously-enabled hash if one is present,
        otherwise raises ValueError
        """
        # default behavior: no way to restore original hash
        raise ValueError("cannot restore original hash")

#=============================================================================
# eof
#=============================================================================
