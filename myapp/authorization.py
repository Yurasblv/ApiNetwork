from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from myapp.models import User

class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            raise AuthenticationFailed('Dont have permission')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Authorization fail!')
        user = User.objects.get(username=payload['user'])
        return user, True
