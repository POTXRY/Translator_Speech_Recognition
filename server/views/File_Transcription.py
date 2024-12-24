import os
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import UPLOAD_FILE_TRANSCRIPTION_DIR
from server.forms import FileUploadForm
from ai_asr.inference import WhisperInference
from server.views.sql_database import db, User, AudioFile  # AudioFile 모델을 추가하여 업로드 정보 저장

bp = Blueprint('File_Transcription', __name__, url_prefix='/File_Transcription')

@bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login.index'))
    
    user = User.query.get(user_id)
    username = user.username if user else "알 수 없음"
    form = FileUploadForm()
    return render_template('File_Transcription.html', form=form, username=username)

def create_time_based_directory(base_dir):
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError("User ID가 세션에 없습니다. 로그인 후 다시 시도하세요.")

    user_dir = os.path.join(base_dir, str(user_id))
    time_dir = datetime.now().strftime('%Y%m%d_%H%M')
    counter = 0
    full_path = os.path.join(user_dir, f"{time_dir}_{counter}")
    
    while os.path.exists(full_path):
        counter += 1
        full_path = os.path.join(user_dir, f"{time_dir}_{counter}")
    
    os.makedirs(full_path, exist_ok=True)
    print(f"[DEBUG] Created directory: {full_path}")
    return full_path

@bp.route('/upload/files/Transcription', methods=['POST'])
def upload():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'fail', 'contents': '로그인이 필요합니다.'}), 403

    print(f'user_id: {user_id}')
    user_upload_dir = create_time_based_directory(UPLOAD_FILE_TRANSCRIPTION_DIR)
    session['user_audio_dir'] = user_upload_dir
    print(f"[DEBUG] Session user_audio_dir: {session['user_audio_dir']}")

    files = request.files.getlist('file')
    for file in files:
        prefix_name = f"{datetime.now().strftime('%y%m%d_%H_%M')}_"
        safe_filename = prefix_name + secure_filename(file.filename)
        file_path = os.path.join(user_upload_dir, safe_filename)
        file.save(file_path)

        # 업로드 정보 데이터베이스에 저장
        upload_entry = AudioFile(user_id=user_id, file_path=file_path)
        db.session.add(upload_entry)
        db.session.commit()
    
    return {'status': 'upload success'}

@bp.route('/process', methods=['POST'])
def process():
    user_id = session.get('user_id')
    user_audio_dir = session.get('user_audio_dir')
    if not user_id or not user_audio_dir:
        return jsonify({
            'status': 'fail',
            'contents': '사용자 식별에 실패했습니다. 다시 시도해 주세요...'
        })

    print(f"[DEBUG] user_id: {user_id}")

    if not os.path.exists(user_audio_dir):
        return jsonify({
            'status': 'fail',
            'contents': '사용자 파일 경로가 존재하지 않습니다. 다시 시도해 주세요...'
        })

    audio_files = os.listdir(user_audio_dir)
    if len(audio_files) == 0:
        return jsonify({
            'status': 'fail',
            'contents': '서버에 처리할 파일이 없습니다. 다시 시도해 주세요...'
        })

    # 결과 저장할 디렉토리 생성
    result_dir = user_audio_dir + "_transcription"
    os.makedirs(result_dir, exist_ok=True)
    print(f"[DEBUG] Result directory created: {result_dir}")

    result_dic = {'length': len(audio_files)}
    for idx, audio in enumerate(audio_files):
        try:
            whisper = WhisperInference()
            target_file = os.path.join(user_audio_dir, audio)
            transcript = whisper.inference(target_file)
            transcript = transcript.replace('. ', '.\n')

            result_filepath = os.path.join(result_dir, f"{audio}_transcription.txt")
            with open(result_filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)

            # 처리 결과 데이터베이스에 업데이트
            audio_entry = AudioFile.query.filter_by(user_id=user_id, file_path=target_file).first()
            if audio_entry:
                audio_entry.result = transcript
                db.session.commit()

            result_dic[f'{idx}'] = transcript
        except Exception as e:
            print(f"[ERROR] Processing failed for file {audio}: {e}")
            result_dic[f'{idx}'] = "처리 실패"

    return jsonify(result_dic)
