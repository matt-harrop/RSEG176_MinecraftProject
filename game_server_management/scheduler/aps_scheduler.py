from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail

from game_server_management.scheduler import aws_ec2_server_scheduler


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(aws_ec2_server_scheduler.start_stop_servers, 'interval', minutes=15)
    # scheduler.add_job(test_job, 'interval', minutes=1)
    scheduler.start()


def test_job():
    send_mail(
        'TestEmail',
        'This is a message testing the automated Python Scheduler.',
        'messages@longlookconsulting.com',
        ['osaintspreserveus@live.com'],
        fail_silently=False
    )
