from peewee import *  # type: ignore
from .db2 import *

# procore
class ProcoreGeneralContractor(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')

    company_id = CharField(unique=True)
    company_name = CharField()


class ProcoreProject(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')
    pjd_general_contractor = ForeignKeyField(ProcoreGeneralContractor, on_delete='CASCADE')

    project_id = CharField(unique=True)
    project_name = CharField()


class ProcoreFile(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')
    procore_general_contractor = ForeignKeyField(ProcoreGeneralContractor, on_delete='CASCADE')
    pjd_project = ForeignKeyField(PjdProject, on_delete='CASCADE')
    procore_project = ForeignKeyField(ProcoreProject, on_delete='CASCADE')
    coord_file = ForeignKeyField(PjdFile, on_delete='CASCADE')

    model_id = CharField(unique=True)
    model_name = CharField()
    version = IntegerField()
    datetime_recieved = DateTimeField()
