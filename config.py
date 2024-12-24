'''Config for flask app (server)'''

import os
from secret import csrf_token_secret



BASE_DIR = os.path.dirname(__file__)
BASESQL_DIR = os.path.abspath(os.path.dirname(__file__))


DB_DIR = os.path.join(BASE_DIR, 'server/static/Database')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)



# secret key for CSRF token
SECRET_KEY = csrf_token_secret

# file transfer config
UPLOAD_FILE_TRANSCRIPTION_DIR = os.path.join(BASE_DIR, 'server/static/files/upload/files/Transcription')
UPLOAD_FILE_TRANSLATE_DIR = os.path.join(BASE_DIR, 'server/static/files/upload/files/Translation')
UPLOAD_LIVE_FILE_DIR = os.path.join(BASE_DIR, 'server/static/files/upload/live')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASESQL_DIR, 'server/static/Database', 'database.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_PROFILE_FILE = os.path.join(BASE_DIR, 'server/static/files/upload/profile')

UPLOAD_AUDIO_FILE_DIR = 'server/static/files/upload/audio'  # 실제 경로로 변경
TEMP_FILE_DIR = os.path.join(BASE_DIR, 'server/static/files/temp')

# ASR model upload directory (especially for Whisper model)
ASR_MODEL_DIR = os.path.join(BASE_DIR, 'ai_asr/models')

# ASR file (ex: .mp3) uploaded from client
CLIENT_AUDIO_UPLOAD_DIR = os.path.join(BASE_DIR, 'server/static/files/asr')

# TODO