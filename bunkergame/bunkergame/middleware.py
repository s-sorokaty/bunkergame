from django.http import HttpResponseRedirect


class AuthRequiredMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to=('acconts/login')) # or http response
        return None