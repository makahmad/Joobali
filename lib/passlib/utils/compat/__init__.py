"""passlib.utils.compat - python 2/3 compatibility helpers"""
#=============================================================================
# figure out what we're running
#=============================================================================

#------------------------------------------------------------------------
# python version
#------------------------------------------------------------------------
import sys
PY2 = sys.version_info < (3,0)
PY3 = sys.version_info >= (3,0)

# make sure it's not an unsupported version, even if we somehow got this far
if sys.version_info < (2,6) or (3,0) <= sys.version_info < (3,2):
    raise RuntimeError("Passlib requires Python 2.6, 2.7, or >= 3.2 (as of passlib 1.7)")

PY26 = sys.version_info < (2,7)

#------------------------------------------------------------------------
# python implementation
#------------------------------------------------------------------------
JYTHON = sys.platform.startswith('java')

PYPY = hasattr(sys, "pypy_version_info")

if PYPY and sys.pypy_version_info < (2,0):
    raise RuntimeError("passlib requires pypy >= 2.0 (as of passlib 1.7)")

# e.g. '2.7.7\n[Pyston 0.5.1]'
PYSTON = "Pyston" in sys.version

#=============================================================================
# common imports
#=============================================================================
import logging; log = logging.getLogger(__name__)
if PY3:
    import builtins
else:
    import __builtin__ as builtins

def add_doc(obj, doc):
    """add docstring to an object"""
    obj.__doc__ = doc

#=============================================================================
# the default exported vars
#=============================================================================
__all__ = [
    # python versions
    'PY2', 'PY3', 'PY26',

    # io
    'BytesIO', 'StringIO', 'NativeStringIO', 'SafeConfigParser',
    'print_',

    # type detection
##    'is_mapping',
    'int_types',
    'num_types',
    'unicode_or_bytes_types',
    'native_string_types',

    # unicode/bytes types & helpers
    'u',
    'unicode',
    'uascii_to_str', 'bascii_to_str',
    'str_to_uascii', 'str_to_bascii',
    'join_unicode', 'join_bytes',
    'join_byte_values', 'join_byte_elems',
    'byte_elem_value',
    'iter_byte_values',

    # iteration helpers
    'irange', #'lrange',
    'imap', 'lmap',
    'iteritems', 'itervalues',
    'next',

    # collections
    'OrderedDict',

    # introspection
    'get_method_function', 'add_doc',
]

# begin accumulating mapping of lazy-loaded attrs,
# 'merged' into module at bottom
_lazy_attrs = dict()

#=============================================================================
# unicode & bytes types
#=============================================================================
if PY3:
    unicode = str

    # TODO: once we drop python 3.2 support, can use u'' again!
    def u(s):
        assert isinstance(s, str)
        return s

    unicode_or_bytes_types = (str, bytes)
    native_string_types = (unicode,)

else:
    unicode = builtins.unicode

    def u(s):
        assert isinstance(s, str)
        return s.decode("unicode_escape")

    unicode_or_bytes_types = (basestring,)
    native_string_types = (basestring,)

# unicode -- unicode type, regardless of python version
# bytes -- bytes type, regardless of python version
# unicode_or_bytes_types -- types that text can occur in, whether encoded or not
# native_string_types -- types that native python strings (dict keys etc) can occur in.

#=============================================================================
# unicode & bytes helpers
#=============================================================================
# function to join list of unicode strings
join_unicode = u('').join

# function to join list of byte strings
join_bytes = b''.join

if PY3:
    def uascii_to_str(s):
        assert isinstance(s, unicode)
        return s

    def bascii_to_str(s):
        assert isinstance(s, bytes)
        return s.decode("ascii")

    def str_to_uascii(s):
        assert isinstance(s, str)
        return s

    def str_to_bascii(s):
        assert isinstance(s, str)
        return s.encode("ascii")

    join_byte_values = join_byte_elems = bytes

    def byte_elem_value(elem):
        assert isinstance(elem, int)
        return elem

    def iter_byte_values(s):
        assert isinstance(s, bytes)
        return s

    def iter_byte_chars(s):
        assert isinstance(s, bytes)
        # FIXME: there has to be a better way to do this
        return (bytes([c]) for c in s)

else:
    def uascii_to_str(s):
        assert isinstance(s, unicode)
        return s.encode("ascii")

    def bascii_to_str(s):
        assert isinstance(s, bytes)
        return s

    def str_to_uascii(s):
        assert isinstance(s, str)
        return s.decode("ascii")

    def str_to_bascii(s):
        assert isinstance(s, str)
        return s

    def join_byte_values(values):
        return join_bytes(chr(v) for v in values)

    join_byte_elems = join_bytes

    byte_elem_value = ord

    def iter_byte_values(s):
        assert isinstance(s, bytes)
        return (ord(c) for c in s)

    def iter_byte_chars(s):
        assert isinstance(s, bytes)
        return s

add_doc(uascii_to_str, "helper to convert ascii unicode -> native str")
add_doc(bascii_to_str, "helper to convert ascii bytes -> native str")
add_doc(str_to_uascii, "helper to convert ascii native str -> unicode")
add_doc(str_to_bascii, "helper to convert ascii native str -> bytes")

# join_byte_values -- function to convert list of ordinal integers to byte string.

# join_byte_elems --  function to convert list of byte elements to byte string;
#                 i.e. what's returned by ``b('a')[0]``...
#                 this is b('a') under PY2, but 97 under PY3.

# byte_elem_value -- function to convert byte element to integer -- a noop under PY3

add_doc(iter_byte_values, "iterate over byte string as sequence of ints 0-255")
add_doc(iter_byte_chars, "iterate over byte string as sequence of 1-byte strings")

#=============================================================================
# numeric
#=============================================================================
if PY3:
    int_types = (int,)
    num_types = (int, float)
else:
    int_types = (int, long)
    num_types = (int, long, float)

#=============================================================================
# iteration helpers
#
# irange - range iterable / view (xrange under py2, range under py3)
# lrange - range list (range under py2, list(range()) under py3)
#
# imap - map to iterator
# lmap - map to list
#=============================================================================
if PY3:
    irange = range
    ##def lrange(*a,**k):
    ##    return list(range(*a,**k))

    def lmap(*a, **k):
        return list(map(*a,**k))
    imap = map

    def iteritems(d):
        return d.items()
    def itervalues(d):
        return d.values()

    def nextgetter(obj):
        return obj.__next__

    izip = zip

else:
    irange = xrange
    ##lrange = range

    lmap = map
    from itertools import imap, izip

    def iteritems(d):
        return d.iteritems()
    def itervalues(d):
        return d.itervalues()

    def nextgetter(obj):
        return obj.next

add_doc(nextgetter, "return function that yields successive values from iterable")

#=============================================================================
# typing
#=============================================================================
##def is_mapping(obj):
##    # non-exhaustive check, enough to distinguish from lists, etc
##    return hasattr(obj, "items")

#=============================================================================
# introspection
#=============================================================================
if PY3:
    method_function_attr = "__func__"
else:
    method_function_attr = "im_func"

def get_method_function(func):
    """given (potential) method, return underlying function"""
    return getattr(func, method_function_attr, func)

def get_unbound_method_function(func):
    """given unbound method, return underlying function"""
    return func if PY3 else func.__func__

def suppress_cause(exc):
    """
    backward compat hack to suppress exception cause in python3.3+

    one python < 3.3 support is dropped, can replace all uses with "raise exc from None"
    """
    exc.__cause__ = None
    return exc

#=============================================================================
# input/output
#=============================================================================
if PY3:
    _lazy_attrs = dict(
        BytesIO="io.BytesIO",
        UnicodeIO="io.StringIO",
        NativeStringIO="io.StringIO",
        SafeConfigParser="configparser.ConfigParser",
    )

    print_ = getattr(builtins, "print")

else:
    _lazy_attrs = dict(
        BytesIO="cStringIO.StringIO",
        UnicodeIO="StringIO.StringIO",
        NativeStringIO="cStringIO.StringIO",
        SafeConfigParser="ConfigParser.SafeConfigParser",
    )

    def print_(*args, **kwds):
        """The new-style print function."""
        # extract kwd args
        fp = kwds.pop("file", sys.stdout)
        sep = kwds.pop("sep", None)
        end = kwds.pop("end", None)
        if kwds:
            raise TypeError("invalid keyword arguments")

        # short-circuit if no target
        if fp is None:
            return

        # use unicode or bytes ?
        want_unicode = isinstance(sep, unicode) or isinstance(end, unicode) or \
                       any(isinstance(arg, unicode) for arg in args)

        # pick default end sequence
        if end is None:
            end = u("\n") if want_unicode else "\n"
        elif not isinstance(end, unicode_or_bytes_types):
            raise TypeError("end must be None or a string")

        # pick default separator
        if sep is None:
            sep = u(" ") if want_unicode else " "
        elif not isinstance(sep, unicode_or_bytes_types):
            raise TypeError("sep must be None or a string")

        # write to buffer
        first = True
        write = fp.write
        for arg in args:
            if first:
                first = False
            else:
                write(sep)
            if not isinstance(arg, basestring):
                arg = str(arg)
            write(arg)
        write(end)

#=============================================================================
# collections
#=============================================================================
if PY26:
    _lazy_attrs['OrderedDict'] = 'passlib.utils.compat._ordered_dict.OrderedDict'
else:
    _lazy_attrs['OrderedDict'] = 'collections.OrderedDict'

#=============================================================================
# lazy overlay module
#=============================================================================
from types import ModuleType

def _import_object(source):
    """helper to import object from module; accept format `path.to.object`"""
    modname, modattr = source.rsplit(".",1)
    mod = __import__(modname, fromlist=[modattr], level=0)
    return getattr(mod, modattr)

class _LazyOverlayModule(ModuleType):
    """proxy module which overlays original module,
    and lazily imports specified attributes.

    this is mainly used to prevent importing of resources
    that are only needed by certain password hashes,
    yet allow them to be imported from a single location.

    used by :mod:`passlib.utils`, :mod:`passlib.crypto`,
    and :mod:`passlib.utils.compat`.
    """

    @classmethod
    def replace_module(cls, name, attrmap):
        orig = sys.modules[name]
        self = cls(name, attrmap, orig)
        sys.modules[name] = self
        return self

    def __init__(self, name, attrmap, proxy=None):
        ModuleType.__init__(self, name)
        self.__attrmap = attrmap
        self.__proxy = proxy
        self.__log = logging.getLogger(name)

    def __getattr__(self, attr):
        proxy = self.__proxy
        if proxy and hasattr(proxy, attr):
            return getattr(proxy, attr)
        attrmap = self.__attrmap
        if attr in attrmap:
            source = attrmap[attr]
            if callable(source):
                value = source()
            else:
                value = _import_object(source)
            setattr(self, attr, value)
            self.__log.debug("loaded lazy attr %r: %r", attr, value)
            return value
        raise AttributeError("'module' object has no attribute '%s'" % (attr,))

    def __repr__(self):
        proxy = self.__proxy
        if proxy:
            return repr(proxy)
        else:
            return ModuleType.__repr__(self)

    def __dir__(self):
        attrs = set(dir(self.__class__))
        attrs.update(self.__dict__)
        attrs.update(self.__attrmap)
        proxy = self.__proxy
        if proxy is not None:
            attrs.update(dir(proxy))
        return list(attrs)

# replace this module with overlay that will lazily import attributes.
_LazyOverlayModule.replace_module(__name__, _lazy_attrs)

#=============================================================================
# eof
#=============================================================================
