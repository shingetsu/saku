"""Attached Files Utilities.
"""
#
# Copyright (c) 2009 shinGETsu Project.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import mimetypes

try:
    import PIL.Image
except ImportError:
    PIL = None

__all__ = ['is_valid_image', 'seem_html']


def seem_html(suffix):
    """Suffix seem to be html or not.
    """
    (path_type, null) = mimetypes.guess_type('test.' + suffix)
    return path_type in (
        'text/html',
        'application/xhtml+xml',
    )

def is_valid_image(mimetype, path):
    """Type of path is same as mimetype or not.
    """
    path_suffix = image_type(path)
    if not path_suffix:
        return False
    (path_type, null) = mimetypes.guess_type('test.' + path_suffix)
    if mimetype == path_type:
        return True
    if (path_type == 'image/jpeg') and (mimetype == 'image/pjpeg'):
        return True
    return False

def is_wellknown_image(path):
    path_suffix = image_type(path)
    return path_suffix in (
      'gif',
      'jpeg',
      'png',
    )

def image_type(path):
    if not path:
        return None
    if not PIL:
        return None
    try:
        return PIL.Image.open(path).format.lower()
    except:
        return None
