from flask import Blueprint, render_template, redirect, url_for, flash, session
from server.views.sql_database import User, db, AudioFile
from server.views.auth_utils import admin_required  # 올바른 경로로 데코레이터 임포트

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()  # 모든 사용자 가져오기
    user_data = [
        {
            "user": user,
            "file_count": len(user.audio_files)  # 사용자별 파일 수 계산
        }
        for user in users
    ]
    return render_template('manage_users.html', user_data=user_data)

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'danger')
        return redirect(url_for('admin.manage_users'))

    # 관리자 계정은 삭제 불가
    if user.is_admin:
        flash(f'관리자 계정은 삭제할 수 없습니다.', 'danger')
        return redirect(url_for('admin.manage_users'))

    # 관련된 업로드 파일 삭제
    AudioFile.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    flash(f'{user.username} 님의 계정이 삭제되었습니다.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/user_management')
def user_management():
    users = User.query.all()
    user_data = [
        {
            'user': user,
            'file_count': AudioFile.query.filter_by(user_id=user.id).count()
        }
        for user in users
    ]
    return render_template('manage_users.html', user_data=user_data)




@bp.route('/admin/make_admin/<int:user_id>', methods=['POST'])
@admin_required
def make_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
        flash(f"{user.username} 님이 관리자로 지정되었습니다.")
    else:
        flash("사용자를 찾을 수 없습니다.")
    return redirect(url_for('admin.manage_users'))




