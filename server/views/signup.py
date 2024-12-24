from flask import  Blueprint, request, jsonify, render_template, redirect, url_for
from server.views.sql_database import db, User
import config

bp = Blueprint('signup', __name__, url_prefix='/signup')





@bp.route('/')
def index():
    '''메인 페이지'''
    
    return render_template(
        'signup.html',
        )



@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 기존 사용자 확인
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({
            "message": "Username or Email already exists"
        }), 400

    # 새 사용자 생성
    new_user = User(username=username, email=email)
    new_user.set_password(password)  # 비밀번호 해싱
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "redirect_url": url_for('login.index'),
        "message": "User created successfully"}), 201