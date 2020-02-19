# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
# Copyright (c) 2020 Mike Kinney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
"""Compatibility code for different versions of python."""
import sys
import operator
import functools

#: Python 3 detection
PY3 = sys.version_info[0] == 3

# Get a reference to the builtins module
try:
    _builtins_ = __import__('builtins')
except ImportError:
    _builtins_ = __import__('__builtin__')

#: Singlular builtin accessor
_builtin = functools.partial(getattr, _builtins_)

#: No operation lambda


def _noop(obj):
    return obj


if PY3:
    meth_func = '__func__'
    raw_input = _builtin('input')

    binary_type = _builtin('bytes')

    # str <-> bytes conversions
    s = operator.methodcaller('decode', 'latin-1')
    b = operator.methodcaller('encode', 'latin-1')

else:
    meth_func = 'im_func'
    raw_input = _builtin('raw_input')

    binary_type = _builtin('str')

    # str <-> bytes conversions (not necessary in python 2)
    s = _noop
    b = _noop


def o(numstr):
    """Octal number compatibility shim."""
    return int(numstr, 8)


def get_meth_func(klass):
    """Get a bound method's function."""
    return operator.attrgetter(
        meth_func)(klass) if hasattr(klass, meth_func) else None


def b2s(bytestr):
    '''"safe" form of ``b``. Checks for binary type before operating.'''
    return s(bytestr) if isinstance(bytestr, binary_type) else bytestr
