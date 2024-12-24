from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    session,
    make_response, current_app as app,
    redirect, url_for, flash
)
from server.views.sql_database import db, User
from werkzeug.security import check_password_hash
import jwt
import datetime
from server.views.auth_utils import admin_required




bp = Blueprint('login', __name__, url_prefix='/login')


bp.secret_key = 'your_secret_key'  # 세션을 위해 필요


@bp.route('/')
def index():
    '''메인 페이지'''
    
    return render_template(
        'login.html',
        )




@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):  # 비밀번호 검증
            # 세션에 사용자 정보 저장
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin  # 관리자 여부 저장

            print(f"[INFO] 사용자 '{user.username}' 로그인 성공 (관리자: {user.is_admin})")  # 로그인 성공 시 콘솔 로그
            return jsonify({'message': 'Logged in successfully', 'redirect_url': url_for('main.index')}), 200
        else:
            print(f"[WARNING] 로그인 실패: 사용자 이름 '{username}' 또는 비밀번호가 올바르지 않음")  # 로그인 실패 시 콘솔 로그
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"[ERROR] 로그인 처리 중 오류 발생: {e}")  # 예외 발생 시 로그
        return jsonify({'message': 'An error occurred during login'}), 500







@bp.route('/admin', methods=['POST'])
def admin():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin  # 관리자 여부 저장
        flash("로그인 성공!")
        return redirect(url_for('profile.profile'))
    else:
        flash("로그인 실패. 이메일 또는 비밀번호를 확인하세요.")
        return redirect(url_for('login.index'))



@bp.route('/logout', methods=['POST'])
def logout():
    # 세션에서 사용자 ID를 먼저 가져와 저장
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # 세션에서 사용자 ID 제거
    session.pop('user_id', None)
    
    # 로그아웃 성공 메시지와 사용자 ID 출력
    print(f"[INFO] '{user.username}' 사용자 로그아웃 성공")
    
    return jsonify({'message': 'Logged out successfully', 'redirect_url': url_for('login.index')})

@bp.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@bp.route('/main')
def main_page():
    if 'user_id' not in session:
        print("[WARNING] 비인증 사용자 접근 시도")
        return redirect(url_for('login'))  # 로그인 페이지로 리다이렉트
    
    # 사용자 정보 조회
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user:
        print(f"[INFO] 인증된 사용자 '{user.username}'가 메인 페이지에 접근함")
        return jsonify({'message': f'Welcome {user.username}!'})
    else:
        return redirect(url_for('login'))



if __name__ == '__main__':
    bp.run(debug=True)



