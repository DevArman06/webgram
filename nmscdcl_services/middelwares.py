
from django.utils.deprecation import MiddlewareMixin
from nmscdcl_services.models import ApiHit

class ApiHitsMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        id = request.path_info.split('/')[-2]
        user = request.user
        # print(request.user.username , 'username')
        # print(request.method , 'METHOD')
        url_paths = [f'/nmscdcl/services/GetLayer/{id}/',
                    '/nmscdcl/auth/test/' ,
                    f'/nmscdcl/services/GetServer/{id}/' ,]
        
        if user.is_authenticated and request.path_info in url_paths:
            try:
                api_hit = ApiHit.objects.get(user=user, url=request.path_info)
            except ApiHit.DoesNotExist:
                api_hit = ApiHit(user=user, url=request.path_info)

            api_hit.count += 1
            api_hit.save()
            # print(f"Hit count for URL {api_hit.url}: {api_hit.count}")

        return response

