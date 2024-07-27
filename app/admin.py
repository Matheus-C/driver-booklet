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
    column_labels = {'name': 'Nome', 'userIdentification': 'Identificação do usuário', 'phone': 'Telefone',
                     'address': 'Endereço', 'email': 'Email', 'birthDate': 'Data de nascimento',
                     'mail_verified': 'email verificado', 'valid_until': 'Válido até'}
    column_exclude_list = '_password'
    column_searchable_list = ('name', 'email')
    column_filters = ('name', 'email')
    can_export = True


class CompanyView(AdminModelView):
    column_display_pk = False
    column_hide_backrefs = False
    column_auto_select_related = True
    column_list = ["owner", "name", "description", "address", "phone", "vatcode"]
    column_labels = {'owner': 'Dono da empresa', 'name': 'Empresa', 'description': 'Descrição',
                     'address': 'Endereço', 'phone': 'Telefone', 'vatcode': 'Vatcode'}
    can_export = True
    column_searchable_list = ('owner.name', 'name', 'vatcode')
    column_filters = ('owner.name', 'name', 'vatcode')


class VehicleView(AdminModelView):
    column_display_pk = False
    column_hide_backrefs = False
    column_auto_select_related = True
    column_list = ["manufacturer", "model", "color", "licensePlate"]
    column_labels = {'model': 'Modelo', 'manufacturer': 'Marca', 'color': 'Cor', 'licensePlate': 'Placa'}
    can_export = True
    column_searchable_list = ('manufacturer', 'model', 'licensePlate')
    column_filters = ('manufacturer', 'model', 'licensePlate')


class AttachmentView(AdminModelView):
    column_display_pk = False
    column_hide_backrefs = False
    column_auto_select_related = True
    column_list = ["user", "company", "vehicle", "type", "start_date", "end_date", "description"]
    column_labels = {'user': 'Usuário', 'company': 'Empresa', 'vehicle': 'Veículo', 'type': 'Tipo',
                     "start_date": "Data início", "end_date": "Data fim", "description": "Descrição"}
    can_export = True
    column_searchable_list = ('user.name', 'company.name', 'vehicle.licensePlate', 'type.name_pt')
    column_filters = ('user.name', 'company.name', 'vehicle.licensePlate', 'type.name_pt', "start_date", "end_date")


class UserCompanyView(AdminModelView):
    column_display_pk = False
    column_hide_backrefs = False
    column_auto_select_related = True
    column_list = ["user", "user.userIdentification", "company", 'company.vatcode', "startWork", "validUntil"]
    column_labels = {'user': 'Usuário', "user.userIdentification": "Identificação do usuário",
                     'company': 'Empresa', "startDate": "Data início", "validUntil": "Válido até"}
    can_export = True
    column_searchable_list = ('user.name', 'user.userIdentification', 'company.name', 'company.vatcode')
    column_filters = ('user.name', 'user.userIdentification', 'company.name', 'company.vatcode',
                      "startWork", "validUntil")


class CompanyVehicleView(AdminModelView):
    column_display_pk = False
    column_hide_backrefs = False
    column_auto_select_related = True
    column_list = ["company", "company.vatcode", "vehicle", "startDate", "validUntil"]
    column_labels = {'company': 'Empresa', "company.vatcode": "Identificação da empresa",
                     "startDate": "Data início", "validUntil": "Válido até"}
    can_export = True
    column_searchable_list = ('company.name', 'company.vatcode', 'vehicle.licensePlate')
    column_filters = ('company.name', 'company.vatcode', 'vehicle.licensePlate', "startDate", "validUntil")


adm.add_view(UserView(User, Session()))
adm.add_view(CompanyView(Company, Session()))
adm.add_view(VehicleView(Vehicle, Session()))
adm.add_view(AttachmentView(Attachment, Session()))
adm.add_view(UserCompanyView(UserCompany, Session()))
adm.add_view(CompanyVehicleView(CompanyVehicle, Session()))
