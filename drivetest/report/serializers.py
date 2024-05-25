from report.models.final_report import FinalReport
from rest_framework import serializers
from course.serializers import SessionSerializer


class FinalReportSerializer(serializers.HyperlinkedModelSerializer):
    session = SessionSerializer()
    class Meta:
        model = FinalReport
        fields = '__all__'