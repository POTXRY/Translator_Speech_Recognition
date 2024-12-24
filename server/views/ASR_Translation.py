from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash
from datetime import datetime
import os
from ai_asr.inference_tr import WhisperInferencetr
from server.forms_tr import FileUploadForm
from config import UPLOAD_LIVE_FILE_DIR, UPLOAD_AUDIO_FILE_DIR
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from server.views.sql_database import User, AudioFile, db

# 디렉토리 생성
os.makedirs(UPLOAD_AUDIO_FILE_DIR, exist_ok=True)

bp = Blueprint('ASR_Translation', __name__, url_prefix='/ASR_Translation')

@bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login.index'))
    
    user = User.query.get(user_id)
    username = user.username if user else "알 수 없음"
    form = FileUploadForm()
    return render_template('ASR_Translation.html', form=form, username=username)







def create_time_based_directory(base_dir, user_id):
    # 사용자 디렉토리 경로 설정
    user_dir = os.path.join(base_dir, str(user_id))
    time_dir = datetime.now().strftime('%Y%m%d_%H%M')
    counter = 0
    full_path = os.path.join(user_dir, f"{time_dir}_{counter}")
    
    # while os.path.exists(full_path):
    #     counter += 1
    #     full_path = os.path.join(user_dir, f"{time_dir}_{counter}")
    
    os.makedirs(full_path, exist_ok=True)
    print(f"[DEBUG] Created directory: {full_path}")
    return full_path








@bp.route('/upload/live', methods=['POST'])
def upload_text():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'No user session available'}), 400

    user_time_dir_text = create_time_based_directory(UPLOAD_LIVE_FILE_DIR, user_id)
    session['user_text_dir'] = user_time_dir_text

    data = request.get_json()
    SpeechRecognition_text = data.get('text')
    if not SpeechRecognition_text:
        return jsonify({'status': 'No text provided'}), 400
    

    SpeechRecognition_text_dir = f"{user_time_dir_text}_SpeechRecognition" 

    os.makedirs(SpeechRecognition_text_dir, exist_ok=True)
    
    SpeechRecognition_Result_filepath = os.path.join(SpeechRecognition_text_dir, "SpeechRecognition_text.txt")
    with open(SpeechRecognition_Result_filepath ,'w', encoding='utf-8') as f:
        f.write(f"음성 인식 결과 : {SpeechRecognition_text}\n")

    print(f"SpeechRecognition Result saved at : {SpeechRecognition_Result_filepath}")



    # 업로드 정보 데이터베이스에 저장
    # upload_entry = AudioFile(user_id=user_id, recognition_result=SpeechRecognition_text)
    # db.session.add(upload_entry)
    # db.session.commit()

    

    # text_filename = "SpeechRecognition_text.txt"
    # text_filepath = os.path.join(user_time_dir_text, text_filename)
    # with open(text_filepath, 'w', encoding='utf-8') as text_file:
    #     text_file.write(text)
    # print(f'Text saved as: {text_filename}')
    # print(f'Session user_text_dir: {session["user_text_dir"]}')
    # print(f"[DEBUG] user_text_dir: {user_time_dir_text}")

    return jsonify({'status': 'Text upload success' }), 200

@bp.route('/upload/audio', methods=['POST'])
def upload_audio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'No user session available'}), 400

    user_time_dir = create_time_based_directory(UPLOAD_AUDIO_FILE_DIR, user_id)
    session['user_audio_dir'] = user_time_dir

    if 'audio' not in request.files:
        return jsonify({'status': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    original_filepath = os.path.join(user_time_dir, "original_audio.webm")
    audio_file.save(original_filepath)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    mp3_filepath = os.path.join(user_time_dir, f"{timestamp}_converted_audio.mp3")
    try:
        audio = AudioSegment.from_file(original_filepath, format="webm")
        audio.export(mp3_filepath, format="mp3")
        print(f"[DEBUG] MP3 file saved as: {mp3_filepath}")
    except Exception as e:
        print(f"[ERROR] Error converting to MP3: {e}")
        return jsonify({'status': 'Failed to convert to MP3', 'error': str(e)}), 500

    if not os.path.exists(mp3_filepath):
        print("[ERROR] MP3 file not created.")
        return jsonify({'status': 'Error', 'contents': 'MP3 file was not created.'}), 500

    # 업로드 정보 데이터베이스에 저장
    

    return jsonify({'status': 'Audio upload success', 'mp3_file': mp3_filepath}), 200


@bp.route('/processtr', methods=['POST'])
def processtr():
    user_id = session.get('user_id')
    user_audio_dir = session.get('user_audio_dir')

    # 세션 값 확인
    print(f"[DEBUG] user_id: {user_id}")
    print(f"[DEBUG] user_audio_dir: {user_audio_dir}")

    if not user_id or not user_audio_dir:
        return jsonify({'status': 'fail', 'contents': '사용자 식별에 실패했습니다.'}), 401

    # 오디오 파일 목록 가져오기
    audio_files = [
        f for f in os.listdir(user_audio_dir)
        if os.path.isfile(os.path.join(user_audio_dir, f)) and f.lower().endswith('.mp3')
    ]

    print(f"Audio files found: {audio_files}")

    if not audio_files:
        return jsonify({'status': 'fail', 'contents': '서버에 처리할 mp3 파일이 없습니다.'}), 404

    result_dic = {}
    translate = None  # 번역 결과를 초기화
    for idx, audio in enumerate(audio_files):
        whisper_tr = WhisperInferencetr()
        target_file = os.path.join(user_audio_dir, audio)
        
        if os.path.isfile(target_file):
            # Whisper를 사용해 번역 수행
            translate = whisper_tr.inference_tr(target_file)
            translate = translate.replace('. ', '.\n')
            result_dic[f'{idx}'] = translate

            # 번역 결과 저장
            save_translation(user_id, translate)
        else:
            print(f"[ERROR] {target_file} is not a valid file.")

    # 첫 번째 파일을 기준으로 데이터베이스에 저장
    if audio_files:
        # 서버 내부 파일 경로를 상대 경로로 변환
        audio_file_path = os.path.relpath(
            os.path.join(user_audio_dir, audio_files[0]), 
            'server/static'
        ).replace("\\", "/")  # Windows에서도 호환되도록 슬래시 정리

        # 업로드 정보 데이터베이스에 저장
        upload_entry = AudioFile(
            user_id=user_id,
            result=translate,
            file_path=f"static/{audio_file_path}"  # 파일 경로에 'files/' 추가
        )
        db.session.add(upload_entry)
        db.session.commit()

    return jsonify(result_dic)




def save_translation(user_id, translation):
    # 시간 기반 디렉토리 생성 후 '_translation'을 추가
    
    time_based_dir = create_time_based_directory(UPLOAD_LIVE_FILE_DIR, user_id)
    
    # 시간 기반 디렉토리 이름 뒤에 '_translation' 추가
    translation_dir = f"{time_based_dir}_translation"
    os.makedirs(translation_dir, exist_ok=True)

    print(f"[DEBUG] Using translation directory: {translation_dir}")

    # 번역 결과 파일 경로 설정
    filepath = os.path.join(translation_dir, "translation_result_text.txt")

    # 번역 결과를 파일에 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"번역 결과: {translation}\n")
    
    print(f"Translation saved successfully at {filepath}")





