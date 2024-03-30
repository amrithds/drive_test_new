from .models import User
from .models import Course
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = User
        fields = ['id', 'url', 'name', 'unique_ref_id', 'course', 'rank', 'unit', 'type']
        

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'