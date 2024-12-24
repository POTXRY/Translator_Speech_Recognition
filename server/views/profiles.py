import os
from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from config import UPLOAD_PROFILE_FILE
from server.views.sql_database import AudioFile, db, User

# Blueprint 설정
bp = Blueprint('profile', __name__, url_prefix='/pr')

# 허용되는 이미지 확장자 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    
    # 사용자 ID가 세션에 없는 경우, 로그인 페이지로 리다이렉트
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login.index'))

    # 데이터베이스에서 사용자 정보를 가져옴
    user = User.query.get(user_id)
    audio_files = AudioFile.query.filter_by(user_id=user_id).all()

    # 웹 경로 변환 함수
    def get_web_path(file_path):
        static_dir = os.path.abspath("server/static")  # static 디렉토리 절대 경로
        return os.path.relpath(file_path, static_dir)  # static 디렉토리 기준 상대 경로

    # 파일 정보 리스트 생성
    uploads = [
        {
            "file_path": get_web_path(upload.file_path) if upload.file_path else None,
            "result": upload.result or "결과 없음",
            "upload_time_kst": upload.upload_time_kst.strftime('%Y-%m-%d %H:%M:%S') if upload.upload_time_kst else "시간 없음",
        }
        for upload in audio_files
    ]
    
    # 사용자 정보가 없는 경우 기본 프로필 이미지 경로 설정
    profile_image_url = url_for('static', filename=user.profile_image) if user and user.profile_image else url_for('static', filename='imgs/base_profile.png')

    # 사용자 정보와 파일 리스트를 템플릿으로 전달
    return render_template(
        'profile.html',
        username=user.username if user else "알 수 없음",
        email=user.email if user else "알 수 없음",
        profile_base_image_url=profile_image_url,
        uploads=uploads
    )

@bp.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login.index'))

    file = request.files.get('profile_image')
    if not file or not allowed_file(file.filename):  # 파일 선택 및 확장자 확인
        flash("허용된 확장자의 파일을 선택해주세요.")
        return redirect(url_for('profile.profile'))

    # 파일 이름을 사용자 ID로 설정
    filename = secure_filename(f"user_{user_id}.png")
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile')
    file_path = os.path.join(upload_folder, filename)

    # 디렉토리 생성 (없는 경우)
    os.makedirs(upload_folder, exist_ok=True)

    # 파일 저장
    file.save(file_path)

    # 사용자 테이블에 이미지 경로 업데이트
    user = User.query.get(user_id)
    user.profile_image = f"uploads/profile/{filename}"  # DB에 저장되는 경로
    db.session.commit()

    flash("프로필 이미지가 성공적으로 업로드되었습니다.")
    return redirect(url_for('profile.profile'))



@bp.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('server/static/files', filename, as_attachment=True)
