from report.models.final_report import FinalReport
from rest_framework import serializers
from course.serializers import SessionSerializer
from course.serializers import ObstacleSerializer


class FinalReportSerializer(serializers.HyperlinkedModelSerializer):
    obstacle = ObstacleSerializer()
    session = SessionSerializer()
    class Meta:
        model = FinalReport
        fields = '__all__'