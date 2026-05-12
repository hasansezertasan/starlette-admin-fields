"""Dedicated Starlette app for e2e tests.

Exposes:
- ``app`` — module-level Starlette instance used by the uvicorn subprocess
  fixture (browser tests).
- ``make_app()`` — factory that builds a fresh Starlette + SQLAlchemy
  in-memory engine pair for the in-process TestClient (HTTP round-trip tests).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import IntegerField
from starlette_admin_fields import (
    BootstrapShowPasswordField,
    CKEditor4Field,
    CKEditor5Field,
    SimpleMDEField,
    StarletteAdminFields,
)

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from starlette.requests import Request

KITCHEN_SINK_BASE = "/admin/kitchen-sink"
"""Admin URL prefix for KitchenSinkView routes."""

E2E_SENTINEL = "starlette-admin-fields-e2e-ok"
"""Sentinel string returned by /healthz — used to verify the correct server is running."""


async def _healthz(request: Request) -> PlainTextResponse:
    return PlainTextResponse(E2E_SENTINEL)


class Base(DeclarativeBase):
    pass


class KitchenSink(Base):
    __tablename__ = "kitchen_sink"
    id = Column(Integer, primary_key=True)
    bootstrap_show_password = Column(String, nullable=False)
    ckeditor4 = Column(Text, nullable=False)
    ckeditor5 = Column(Text, nullable=False)
    simplemde = Column(Text, nullable=False)


class KitchenSinkView(ModelView):
    fields = [
        IntegerField(name="id", label="ID", read_only=True),
        BootstrapShowPasswordField(
            name="bootstrap_show_password",
            label="BootstrapShowPasswordField",
            size="md",
        ),
        CKEditor4Field(name="ckeditor4", label="CKEditor4Field"),
        CKEditor5Field(name="ckeditor5", label="CKEditor5Field"),
        SimpleMDEField(name="simplemde", label="SimpleMDEField"),
    ]


def make_app() -> tuple[Starlette, Engine]:
    """Build a fresh Starlette app + in-memory SQLite engine.

    The returned engine is owned by the caller and is the same engine the
    admin reads/writes through, so tests may assert directly on persisted rows.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    starlette_app = Starlette(routes=[Route("/healthz", _healthz)])
    admin = Admin(engine, title="E2E: Fields", base_url="/admin")
    StarletteAdminFields(admin=admin)
    admin.add_view(KitchenSinkView(model=KitchenSink))
    admin.mount_to(starlette_app)
    return starlette_app, engine
