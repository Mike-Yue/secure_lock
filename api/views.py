from django.http import HttpResponseForbidden, HttpResponse
from api.models import Lock, Code, LockUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.serializers import UserSerializerRead, UserSerializerWrite, LockSerializer, LockSerializerCreate, CodeSerializer
from api.permissions import IsMasterUserOnly
from django_filters import rest_framework as filters
from api.filters import CodeFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import secrets
import datetime
from datetime import timezone
from django.db import IntegrityError

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def get_queryset(self):
        user = self.request.user
        return LockUser.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserSerializerWrite
        return UserSerializerRead

class LockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    permission_classes = (IsAuthenticated, IsMasterUserOnly)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LockSerializerCreate
        return LockSerializer

    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        return Lock.objects.filter(users__id=user.id)
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        lock_id = self.request.data['lock_id']
        new_lock = Lock.objects.create(lock_id=lock_id, master_user=user, display_name=request.data['display_name'])
        new_lock.users.set([user])
        return Response(status=status.HTTP_200_OK)


class CodeViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    serializer_class = CodeSerializer

    def get_queryset(self):
        return Code.objects.filter(created_by=self.request.user, expired=False)
    
    def create(self, request, *args, **kwargs):
        target_lock = Lock.objects.get(lock_id=request.data['lock_id'])
        if not target_lock.code_set.filter(expired=False):
            if request.user in target_lock.users.all():
                code_generator = secrets.SystemRandom()
                code = code_generator.randint(0,9999)
                temp = Code.objects.create(
                    code=code, 
                    lock=target_lock,
                    expiry_time=request.data['expiry_time'], 
                    created_by=request.user, 
                    creation_time=datetime.datetime.now(timezone.utc),
                    used_at_time=None,
                    )
                return Response({"Message": "Your code is: {}".format(str(code).zfill(4))}, status=status.HTTP_200_OK)
            else:
                return Response({"Message": "You do not have permissions to create a code for this lock"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"Message": "You already have a code for this lock"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def validate(request):
    if request == "GET":
        return Response({"message": "Hello, world!"})
    else:
        lock_id = request.data['lock_id']
        entry_code = request.data['code']
        try:
            target_code = Code.objects.get(code=int(entry_code))
            target_lock = Lock.objects.get(lock_id=lock_id)
        except:
            return Response({"Error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if target_code.lock == target_lock and not target_code.expired:
            target_code.used_at_time = datetime.datetime.now(timezone.utc)
            target_code.expired = True
            target_code.save()
            return Response({"Message": "Code is valid"}, status=status.HTTP_200_OK)
        return Response({"Error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)