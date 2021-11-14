from django.apps import AppConfig


class GameServerManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game_server_management'

    def ready(self):
        from game_server_management.scheduler import aps_scheduler
        aps_scheduler.start()