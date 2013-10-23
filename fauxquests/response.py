# -*- coding: utf-8 -*-
# This response class is copied, with only slight modifications, from
# Łukasz Langa's `requests_testadapter` package (which was a springboard
# for this project).
#
# Therefore, the following copyright / license notice applies to the code
# in this file:
#
# Copyright (C) 2013 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from six import BytesIO

import requests.status_codes


class Resp(BytesIO):
    def __init__(self, stream, status=200, headers=None):
        self.status = status
        self.headers = headers or {}
        self.reason = requests.status_codes._codes.get(
            status, ['']
        )[0].upper().replace('_', ' ')
        BytesIO.__init__(self, stream)

    @property
    def _original_response(self):
        return self

    @property
    def msg(self):
        return self

    def read(self, chunk_size, **kwargs):
        return BytesIO.read(self, chunk_size)

    def info(self):
        return self

    def get_all(self, name, default):
        result = self.headers.get(name)
        if not result:
            return default
        return [result]

    def getheaders(self, name):
        return self.get_all(name, [])

    def release_conn(self):
        self.close()
