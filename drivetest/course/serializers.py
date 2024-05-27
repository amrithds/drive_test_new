from .models import User
from .models import Course
from .models import Obstacle
from .models import Session
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = User
        fields = ['id', 'url', 'name', 'username', 'unique_ref_id', 'course', 'rank', 'unit', 'type']
        

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class ObstacleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Obstacle
        fields = '__all__'


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    trainee = UserSerializer()
    trainer = UserSerializer()
    class Meta:
        model = Session
        fields = ['id', 'url', 'trainer', 'trainee', 'status', 'mode', 'course', 'created_at']