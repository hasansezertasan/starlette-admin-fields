from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import IntegerField
from starlette_admin_fields import (
    BootstrapShowPasswordField,
    CKEditor4Field,
    CKEditor5Field,
    SimpleMDEField,
    StarletteAdminFields,
)

Base = declarative_base()

engine = create_engine(
    "sqlite:///db.sqlite3",
    connect_args={"check_same_thread": False},
    echo=True,
)


class KitchenSink(Base):
    __tablename__ = "kitchen_sink"
    id = Column(Integer, primary_key=True)
    bootstra_show_password = Column(String, nullable=False)
    ckeditor4 = Column(Text, nullable=False)
    ckeditor5 = Column(Text, nullable=False)
    simplemde = Column(Text, nullable=False)



class KitchenSinkView(ModelView):
    fields = [
        IntegerField(
            name="id",
            label="ID",
            read_only=True,
        ),
        BootstrapShowPasswordField(
            name="bootstra_show_password",
            label="BootstrapShowPasswordField",
            size="md",
        ),
        CKEditor4Field(
            name="ckeditor4",
            label="CKEditor4Field",
        ),
        CKEditor5Field(
            name="ckeditor5",
            label="CKEditor5Field",
        ),
        SimpleMDEField(
            name="simplemde",
            label="SimpleMDEField",
        ),
    ]


def init_database() -> None:
    Base.metadata.create_all(engine)


app = Starlette(on_startup=[init_database])

# Create admin
admin = Admin(engine, title="Example: Fields", base_url="/")

# Extend Admin
StarletteAdminFields(admin=admin)

# Add views
admin.add_view(KitchenSinkView(model=KitchenSink))

# Mount admin
admin.mount_to(app)
