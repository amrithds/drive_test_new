from report.models.final_report import FinalReport
from rest_framework import serializers


class FinalReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FinalReport
        fields = '__all__'