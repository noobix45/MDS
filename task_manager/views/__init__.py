#views/__init__.py a devenit sub pachet care poate fi importat

from .home_views import home, register, login_view, logout_view, delete_account
from .task_views import create_task,delete_tasks, edit_task, update_task_completion,delete_task
from .delete_notif import delete_notificare_api
from .ai_views import ai_prioritize_user_tasks
from .mail_views import send_email_mailjet
# from .group_views import create_group, group_detail