# -*- coding: utf-8 -*-
# pylint: disable-msg=
"""
Created on Mon May 28 16:40:37 2012

This module provides a utility function to define declarative constraints.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.

@author: T. Teijeiro
"""

def verify(expression, messagestr = None, messageargs = None):
    """
    This function provides an equivalent functionality to the *assert* builtin,
    but it cannot be disabled at compile time. It is very useful to check if a
    proposition is true, raising an *InconsistencyError* otherwise.

    Parameters
    ----------
    expression:
        Boolean expression. If it is True, the function does nothing, else it
        raises an InconsistencyError.
    messagestr:
        Optional message string to explain the generated exception, if it is
        the case.
    messageargs:
        List or tuple of arguments that are passed to the *format* method of
        messagestr. The string is only built if the exception is generated.
    """
    messageargs = messageargs or []
    if not expression:
        raise (InconsistencyError() if messagestr is None
                      else InconsistencyError(messagestr.format(*messageargs)))


class InconsistencyError(Exception):
    """Exception raised when a constraint verification fails"""
    pass


if __name__ == "__main__":
    pass