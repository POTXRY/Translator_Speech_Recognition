import config
from flask import Flask
from ai_asr.inference import WhisperInference
from ai_asr.inference_tr import WhisperInferencetr
from server.views.sql_database import db
from flask_migrate import Migrate
from .views.sql_database import db  # db 인스턴스를 가져옴


# Create whisper objectr
whisper = WhisperInference()
whisper_tr = WhisperInferencetr()




def create_app() -> Flask:
    '''서비스용 앱 생성'''
    app = Flask(__name__)
    app.config.from_object(config)

    # SQLAlchemy 인스턴스를 Flask 앱과 연결
    db.init_app(app)
    Migrate(app, db)  # Flask-Migrate 설정 추가

    # Flask 애플리케이션 컨텍스트 내에서 데이터베이스 생성
    with app.app_context():
        db.create_all()

    # Blueprint 등록
    from .views import main_views
    from .views import File_Transcription
    from .views import ASR_Translation
    from .views import File_Translation
    from .views import login
    from .views import signup
    from .views import profiles
    from .views import admin
    app.register_blueprint(main_views.bp)
    app.register_blueprint(File_Transcription.bp)
    app.register_blueprint(ASR_Translation.bp)
    app.register_blueprint(File_Translation.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(signup.bp)
    app.register_blueprint(profiles.bp)
    app.register_blueprint(admin.bp)

    return app