# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(http_method_names=['GET','POST'])
def test_view(request):
    data = {'t':1}
    return Response(data)
