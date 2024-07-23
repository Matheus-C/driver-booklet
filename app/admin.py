from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from app import adm
from app.models.models import *


class AdminModelView(ModelView):
    create_modal = True
    edit_modal = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.userTypeId == 3


class UserView(AdminModelView):
    column_searchable_list = ('name', 'email')
    column_filters = ('name', 'email')
    can_export = True


adm.add_view(UserView(User, Session()))
adm.add_view(AdminModelView(Event, Session()))
adm.add_view(AdminModelView(Attachment, Session()))
adm.add_view(AdminModelView(Company, Session()))
adm.add_view(AdminModelView(Vehicle, Session()))
