from rest_framework import serializers
from api.models import Lock, Code, LockUser

class UserSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = LockUser
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class UserSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = LockUser
        fields = ["id", "username", "email"]

class LockSerializer(serializers.ModelSerializer):
    master_user = UserSerializerRead(read_only=True)
    users = UserSerializerRead(many=True, read_only=True)
    class Meta:
        model = Lock
        fields = "__all__"

class LockSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = "__all__"


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = "__all__"