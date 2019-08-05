import datetime, json
from rest_framework.response import Response
from rest_framework.views import APIView

from seo_app import models


class EventProductCreate(APIView):

    def post(self, request, *args, **kwargs):
        print("------------ order paid ------------:")
        print(json.dumps(request.data))
        return Response({"code": 200})


class EventProductUpdate(APIView):
    def post(self, request, *args, **kwargs):
        print("------------ Customer Create ------------:")
        # print(request.META, type(request.META))
        print(json.dumps(request.data))
        return Response({"code": 200})


