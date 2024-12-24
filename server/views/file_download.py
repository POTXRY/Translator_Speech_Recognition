from flask import Blueprint, send_from_directory, abort
import os

bp = Blueprint('file_download', __name__, url_prefix='/download')

@bp.route('/<path:filename>', methods=['GET'])
def download_file(filename):
    upload_dir = "server/static/files/upload/audio"  # 파일 저장 디렉토리
    file_path = os.path.join(upload_dir, filename)
    
    if not os.path.exists(file_path):
        abort(404)  # 파일이 없으면 404 에러 반환

    return send_from_directory(upload_dir, filename, as_attachment=True)
