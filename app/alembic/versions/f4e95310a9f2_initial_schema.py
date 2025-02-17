"""initial schema

Revision ID: f4e95310a9f2
Revises: 
Create Date: 2025-02-17 11:22:31.265342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = 'f4e95310a9f2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 기존 SQL 파일 실행
    sql_file_path = os.path.join(os.path.dirname(__file__), "init_database.sql")
    with open(sql_file_path, "r") as file:
        sql_commands = file.read()
    
    # SQL 실행
    op.execute(sql_commands)

def downgrade():
    # 필요에 따라 롤백 SQL을 정의할 수도 있음
    pass
