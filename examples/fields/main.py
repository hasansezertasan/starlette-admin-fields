from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import IntegerField
from starlette_admin_fields import (
    BootstrapShowPasswordField,
    CKEditor4Field,
    CKEditor5Field,
    SimpleMDEField,
    extend_admin,
)

from .database import Base, KitchenSink, engine


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
            size="lg",
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
extend_admin(admin)

# Add views
admin.add_view(KitchenSinkView(model=KitchenSink))

# Mount admin
admin.mount_to(app)
