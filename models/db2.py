from enum import Enum
from peewee import *  # type: ignore

db = SqliteDatabase('test.db')

class FileSources(Enum):
    OTHER = 0
    GLUE = 1
    PROCORE = 2

class FileTypes(Enum):
    OTHER = 0
    DWG = 1
    RVT = 2
    DWF = 3
    PDF = 4

class BaseModel(Model):
    class Meta:
        database = db


# generic
class GeneralContractor(BaseModel):
    name = CharField(unique=True)


class PjdProject(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')

    project_nuber = CharField(unique=True)
    project_name = CharField()


class PjdFile(BaseModel):
    general_contractor = ForeignKeyField(GeneralContractor, on_delete='CASCADE')
    pjd_project = ForeignKeyField(PjdProject, on_delete='CASCADE')

    source = IntegerField(choices=FileSources)
    file_type = IntegerField(choices=FileTypes)
    filepath = CharField()
