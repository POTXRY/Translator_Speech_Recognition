from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)  # 프로필 이미지 경로
    is_admin = db.Column(db.Boolean, default=False)  # 관리자 여부 필드 추가

    # 오디오 파일 경로와 처리 결과
    audio_file_path = db.Column(db.String(200), nullable=True)  # 오디오 파일 경로
    audio_result = db.Column(db.Text, nullable=True)  # 처리 결과

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



    # 관계 설정
    audio_files = db.relationship('AudioFile', backref='user', lazy=True)

class AudioFile(db.Model):
    __tablename__ = 'audio_files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=True)  # 파일 경로
    result = db.Column(db.Text, nullable=True)  # 새로 추가된 칼럼
    recognition_result = db.Column(db.Text, nullable=True)  # 음성인식 결과
    translation_result = db.Column(db.Text, nullable=True)  # 번역 결과
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)  # 업로드 시간
    processed_time = db.Column(db.DateTime, default=datetime.utcnow)  # 처리 시간
    


    @property
    def upload_time_kst(self):
        return self.upload_time + timedelta(hours=9)