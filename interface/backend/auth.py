from django.contrib.auth.models import User

class VmckAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            newUser = User.objects.get(username=username)
        except User.DoesNotExist:
            newUser = User.objects.create_user(username=username, password=password)

        return newUser

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
