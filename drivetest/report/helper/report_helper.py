from report.models.sensor_feed import SensorFeed
from django.db.models import Max, Min

def get_obstacle_duration(obstacle_id: int) -> dict:
    obstacle_duration = {"obstacle_duration": """TIMESTAMPDIFF(SECOND,  MIN(created_at), MAX(created_at))"""}
    feed_obj = SensorFeed.objects.extra(select=obstacle_duration).values('obstacle_duration').filter(obstacle_id=obstacle_id)
    print(feed_obj[0])
    if feed_obj:
        return feed_obj[0]['obstacle_duration']
    return 0