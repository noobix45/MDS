#views/__init__.py a devenit sub pachet care poate fi importat

from .home_views import home, register, login_view, logout_view
from .task_views import create_task,delete_tasks, edit_task, update_task_completion
# from .task_views import create_task, task_detail
# from .group_views import create_group, group_detail