from django.conf import settings
from django.utils import translation

# class ForceDefaultLanguageMiddleware:

#     def process_request(self, request):
#         request.LANG = getattr(settings, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
#         translation.activate(request.LANG)
#         request.LANGUAGE_CODE = request.LANG

# class ForceDefaultLanguageMiddleware(object):
#     """
#     Ignore Accept-Language HTTP headers
    
#     This will force the I18N machinery to always choose settings.LANGUAGE_CODE
#     as the default initial language, unless another one is set via sessions or cookies
    
#     Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
#     namely django.middleware.locale.LocaleMiddleware
#     """
#     def process_request(self, request):
#         if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
#             del request.META['HTTP_ACCEPT_LANGUAGE']


# For Django 1.10 - 2.0 (and Python 3) its now:
def force_default_language_middleware(get_response):
    """
        Ignore Accept-Language HTTP headers
        This will force the I18N machinery to always choose settings.LANGUAGE_CODE
        as the default initial language, unless another one is set via sessions or cookies
        Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
        namely django.middleware.locale.LocaleMiddleware
        """
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware