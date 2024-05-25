import django_filters
from report.models.final_report import FinalReport

class FinalReportFilter(django_filters.FilterSet):
    class Meta:
        model = FinalReport
        fields = ['trainee', 'trainer', 'session']