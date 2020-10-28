from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

from .models import Maintenance


currencies = {
    "KE":1,
    "US":0.00925
}


class ComingSoonMiddleware(object):

    def __init__(self,get_response):
        self.get_response = get_response


    def __call__(self,request):
        under_maintenance = Maintenance.objects.all().filter(maintained=True)
        path = request.get_full_path()
        if under_maintenance and "/admin/" not in path:
            return JsonResponse({"maintenance":True},status=503)
        return self.get_response(request)


class CurrencyMiddleware(object):

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        currency = request.headers.get("cur")
        if currency:
            try:
                currency_value = currencies["currency"]
            except KeyError:
                currency_value = currencies["KE"]
        else:
            currency_value = currencies["KE"]
        response = self.get_response(request)
        if isinstance(response,Response):
            response.data["cur"] = currency_value
            response._is_rendered = False
            response.render()
        return response