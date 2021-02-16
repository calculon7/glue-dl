from peewee import *  # type: ignore
from .db2 import *

# glue
class GlueGeneralContractor(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')

    company_id = CharField(unique=True)
    company_guid = CharField(unique=True)
    company_name = CharField()


class GlueProject(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')
    glue_general_contractor = ForeignKeyField(GlueGeneralContractor, on_delete='CASCADE')

    project_id = CharField(unique=True)
    project_name = CharField()


class GlueFile(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')
    glue_general_contractor = ForeignKeyField(GlueGeneralContractor, on_delete='CASCADE')
    pjd_project = ForeignKeyField(PjdProject, on_delete='CASCADE')
    glue_project = ForeignKeyField(GlueProject, on_delete='CASCADE')
    coord_file = ForeignKeyField(PjdFile, on_delete='CASCADE')

    
    model_id = CharField(unique=True)
    model_name = CharField()
    version = IntegerField()
    datetime_recieved = DateTimeField()
