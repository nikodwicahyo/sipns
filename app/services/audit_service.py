from app.models.audit_log import AuditLog
from app import db


def catat_audit_log(user_id, action, table_name, record_id=None, description=None, ip_address=None):
    AuditLog.log(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        description=description,
        ip_address=ip_address,
    )
