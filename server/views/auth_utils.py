from functools import wraps
from flask import session, abort
from server.views.sql_database import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            abort(403)  # 관리자 권한이 없으면 접근 금지
        return f(*args, **kwargs)
    return decorated_function


