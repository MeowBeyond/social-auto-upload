import os
import urllib.request
import urllib.parse
import cgi
from urllib.parse import urlparse
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory
from app.core.config import BASE_DIR
from app.core.db import get_db

file_bp = Blueprint('file', __name__)

@file_bp.route('/social/api/upload', methods=['POST'])
def upload_file():
    try:
        # 检查是否为基于URL上传
        if 'url' in request.form:
            url = request.form['url']
            if not url:
                return jsonify({
                    "code": 400,
                    "data": None,
                    "msg": "URL parameter is empty"
                }), 400
                
            try:
                print(f"Downloading from URL: {url}")
                
                # 增加 User-Agent 头，防止被服务器拒绝
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                )
                
                with urllib.request.urlopen(req) as response:
                    # 尝试从 Content-Disposition 响应头中获取文件名
                    filename = None
                    content_disposition = response.headers.get('Content-Disposition')
                    if content_disposition:
                        _, params = cgi.parse_header(content_disposition)
                        filename = params.get('filename')
                        if filename:
                            filename = filename.strip('"\'')
                    
                    # 如果响应头没有提供，则回退到从 URL 路径解析
                    if not filename:
                        parsed_url = urlparse(url)
                        filename = os.path.basename(parsed_url.path)
                        
                    # 尝试从 Content-Type 推断后缀名
                    if not filename or '.' not in filename:
                        content_type = response.headers.get('Content-Type', '')
                        ext = '.mp4'  # 默认
                        if 'video/webm' in content_type:
                            ext = '.webm'
                        elif 'video/x-matroska' in content_type:
                            ext = '.mkv'
                        elif 'video/quicktime' in content_type:
                            ext = '.mov'
                        elif 'video/x-flv' in content_type:
                            ext = '.flv'
                    elif 'video/x-msvideo' in content_type:
                        ext = '.avi'
                    elif 'video/x-ms-wmv' in content_type:
                        ext = '.wmv'
                        
                    if not filename or filename == "downloaded_video":
                        filename = f"downloaded_video{ext}"
                    else:
                        # 如果从URL解析出来的名字没有后缀，加上推断的后缀
                        if '.' not in filename:
                            filename = f"{filename}{ext}"
    
                    uuid_v1 = uuid.uuid1()
                    final_filename = f"{uuid_v1}_{filename}"
                    filepath = Path(BASE_DIR / "videoFile" / final_filename)
                    
                    # 写入文件
                    with open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                
                return jsonify({"code":200,"msg": "File downloaded successfully", "data": final_filename}), 200
                
            except Exception as e:
                print(f"Download failed: {e}")
                return jsonify({
                    "code": 500,
                    "data": None,
                    "msg": f"Download failed: {e}"
                }), 500

        if 'file' not in request.files:
            return jsonify({
                "code": 400,
                "data": None,
                "msg": "No file part in the request"
            }), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "code": 400,
                "data": None,
                "msg": "No selected file"
            }), 400

        # 保存文件到指定位置
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{file.filename}")
        file.save(filepath)
        return jsonify({"code":200,"msg": "File uploaded successfully", "data": f"{uuid_v1}_{file.filename}"}), 200
    except Exception as e:
        return jsonify({"code":500,"msg": str(e),"data":None}), 500

@file_bp.route('/social/api/getFile', methods=['GET'])
def get_file():
    # 获取 filename 参数
    filename = request.args.get('filename')

    if not filename:
        return jsonify({"code": 400, "msg": "filename is required", "data": None}), 400

    # 防止路径穿越攻击
    if '..' in filename or filename.startswith('/'):
        return jsonify({"code": 400, "msg": "Invalid filename", "data": None}), 400

    # 拼接完整路径
    file_path = str(Path(BASE_DIR / "videoFile"))

    # 返回文件
    return send_from_directory(file_path,filename)


@file_bp.route('/social/api/uploadSave', methods=['POST'])
def upload_save():
    try:
        # 检查是否为基于URL上传
        if 'url' in request.form:
            url = request.form['url']
            if not url:
                return jsonify({
                    "code": 400,
                    "data": None,
                    "msg": "URL parameter is empty"
                }), 400
                
            try:
                # 从URL中提取文件名，如果提取不到则随机生成
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = "downloaded_video.mp4"
                
                # 如果用户传递了自定义文件名，则覆盖
                custom_filename = request.form.get('filename', None)
                if custom_filename:
                    # 尝试保留扩展名
                    ext = filename.split('.')[-1] if '.' in filename else 'mp4'
                    filename = f"{custom_filename}.{ext}"

                uuid_v1 = uuid.uuid1()
                final_filename = f"{uuid_v1}_{filename}"
                filepath = Path(BASE_DIR / "videoFile" / final_filename)
                
                # 下载文件
                print(f"Downloading from URL: {url}")
                
                # 增加 User-Agent 头，防止被服务器拒绝
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                )
                
                with urllib.request.urlopen(req) as response:
                    # 尝试从 Content-Disposition 响应头中获取文件名
                    filename = None
                    content_disposition = response.headers.get('Content-Disposition')
                    if content_disposition:
                        _, params = cgi.parse_header(content_disposition)
                        filename = params.get('filename')
                        if filename:
                            filename = filename.strip('"\'')
                    
                    # 如果响应头没有提供，则回退到从 URL 路径解析
                    if not filename:
                        parsed_url = urlparse(url)
                        filename = os.path.basename(parsed_url.path)
                        
                    # 尝试从 Content-Type 推断后缀名
                    if not filename or '.' not in filename:
                        content_type = response.headers.get('Content-Type', '')
                        ext = '.mp4'  # 默认
                        if 'video/webm' in content_type:
                            ext = '.webm'
                        elif 'video/x-matroska' in content_type:
                            ext = '.mkv'
                        elif 'video/quicktime' in content_type:
                            ext = '.mov'
                        elif 'video/x-flv' in content_type:
                            ext = '.flv'
                    elif 'video/x-msvideo' in content_type:
                        ext = '.avi'
                    elif 'video/x-ms-wmv' in content_type:
                        ext = '.wmv'
                        
                    if not filename or filename == "downloaded_video":
                        filename = f"downloaded_video{ext}"
                    else:
                        # 如果从URL解析出来的名字没有后缀，加上推断的后缀
                        if '.' not in filename:
                            filename = f"{filename}{ext}"
                
                    # 如果用户传递了自定义文件名，则覆盖
                    custom_filename = request.form.get('filename', None)
                    if custom_filename:
                        # 尝试保留扩展名
                        ext = filename.split('.')[-1] if '.' in filename else 'mp4'
                        filename = f"{custom_filename}.{ext}"
    
                    uuid_v1 = uuid.uuid1()
                    final_filename = f"{uuid_v1}_{filename}"
                    filepath = Path(BASE_DIR / "videoFile" / final_filename)
                    
                    # 写入文件
                    with open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                
                # 记录到数据库
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO file_records (filename, filesize, file_path) VALUES (%s, %s, %s)',
                        (filename, round(float(os.path.getsize(filepath)) / (1024 * 1024), 2), final_filename))
                    print("✅ URL下载文件已记录")
                
                return jsonify({
                    "code": 200,
                    "msg": "File downloaded and saved successfully",
                    "data": {
                        "filename": filename,
                        "filepath": final_filename
                    }
                }), 200
                
            except Exception as e:
                print(f"Download failed: {e}")
                return jsonify({
                    "code": 500,
                    "data": None,
                    "msg": f"Download failed: {e}"
                }), 500

        # 如果没有URL，继续常规的文件上传逻辑
        if 'file' not in request.files:
            return jsonify({
                "code": 400,
                "data": None,
                "msg": "No file part in the request"
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "code": 400,
                "data": None,
                "msg": "No selected file"
            }), 400

        # 获取表单中的自定义文件名（可选）
        custom_filename = request.form.get('filename', None)
        if custom_filename:
            filename = custom_filename + "." + file.filename.split('.')[-1]
        else:
            filename = file.filename

        # 生成 UUID v1
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")

        # 构造文件名和路径
        final_filename = f"{uuid_v1}_{filename}"
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{filename}")

        # 保存文件
        file.save(filepath)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO file_records (filename, filesize, file_path) VALUES (%s, %s, %s)',
                (filename, round(float(os.path.getsize(filepath)) / (1024 * 1024), 2), final_filename))
            print("✅ 上传文件已记录")

        return jsonify({
            "code": 200,
            "msg": "File uploaded and saved successfully",
            "data": {
                "filename": filename,
                "filepath": final_filename
            }
        }), 200

    except Exception as e:
        print(f"Upload failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"upload failed: {e}",
            "data": None
        }), 500

@file_bp.route('/social/api/getFiles', methods=['GET'])
def get_all_files():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM file_records")
            rows = cursor.fetchall()

            data = []
            for row in rows:
                row_dict = dict(row)
                if row_dict.get('file_path'):
                    file_path_parts = row_dict['file_path'].split('_', 1)
                    row_dict['uuid'] = file_path_parts[0] if file_path_parts else ''
                else:
                    row_dict['uuid'] = ''
                data.append(row_dict)

            return jsonify({
                "code": 200,
                "msg": "success",
                "data": data
            }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("get file failed!"),
            "data": None
        }), 500

@file_bp.route('/social/api/deleteFile', methods=['GET'])
def delete_file():
    file_id = request.args.get('id')

    if not file_id or not file_id.isdigit():
        return jsonify({
            "code": 400,
            "msg": "Invalid or missing file ID",
            "data": None
        }), 400

    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM file_records WHERE id = %s", (file_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "File not found",
                    "data": None
                }), 404

            file_path = Path(BASE_DIR / "videoFile" / record['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"✅ 实际文件已删除: {file_path}")
                except Exception as e:
                    print(f"⚠️ 删除实际文件失败: {e}")
            else:
                print(f"⚠️ 实际文件不存在: {file_path}")

            cursor.execute("DELETE FROM file_records WHERE id = %s", (file_id,))

        return jsonify({
            "code": 200,
            "msg": "File deleted successfully",
            "data": {
                "id": record['id'],
                "filename": record['filename']
            }
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500
