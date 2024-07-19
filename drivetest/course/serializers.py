from .models import User
from .models import Course
from .models import Obstacle,ObstacleTaskScore,Task
from .models import Session
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'name')

class ObstacleTaskScoreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='task.name')
    result = serializers.SerializerMethodField()

    class Meta:
        model = ObstacleTaskScore
        fields = ('id', 'name', 'result')
    def get_result(self, obj):
        return 0
class UserSerializer(serializers.HyperlinkedModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = User
        fields = ['id', 'url', 'name', 'username', 'unique_ref_id', 'course', 'rank', 'unit', 'type','serial_no']
        

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']

class ObstacleSerializer(serializers.ModelSerializer):
    obstacletaskscore_set = ObstacleTaskScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Obstacle
        fields = '__all__'


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    trainee = UserSerializer()
    trainer = UserSerializer()
    class Meta:
        model = Session
        fields = ['id', 'url', 'trainer', 'trainee', 'status', 'mode', 'course', 'created_at']