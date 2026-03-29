import os
import uuid
import urllib.request
import cgi
from urllib.parse import urlparse
from pathlib import Path
from flask import Blueprint, request, jsonify
from app.services.postVideo import post_video_tencent, post_video_DouYin, post_video_ks, post_video_xhs
from app.core.config import BASE_DIR

publish_bp = Blueprint('publish', __name__)

def download_video_urls(file_urls):
    downloaded_filenames = []
    # 确保 videoFile 目录存在
    video_dir = Path(BASE_DIR / "videoFile")
    video_dir.mkdir(parents=True, exist_ok=True)
    
    for url in file_urls:
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
                    # 清理可能带有的引号
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
                filepath = video_dir / final_filename
                
                # 写入文件
                with open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
                
            downloaded_filenames.append(final_filename)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            raise Exception(f"Failed to download {url}: {e}")
    return downloaded_filenames

def cleanup_downloaded_files(filenames):
    for filename in filenames:
        try:
            filepath = Path(BASE_DIR / "videoFile" / filename)
            if filepath.exists():
                filepath.unlink()
                print(f"✅ Cleaned up downloaded file: {filepath}")
        except Exception as e:
            print(f"⚠️ Failed to clean up file {filename}: {e}")

@publish_bp.route('/social/api/postVideo', methods=['POST'])
def postVideo():
    # 获取JSON数据
    data = request.get_json()

    if not data:
        return jsonify({"code": 400, "msg": "请求数据不能为空", "data": None}), 400

    # 从JSON数据中提取fileList和accountList
    file_list = data.get('fileList', [])
    file_urls = data.get('fileUrls', [])
    account_list = data.get('accountList', [])
    type = data.get('type')
    title = data.get('title')
    tags = data.get('tags', [])
    category = data.get('category')
    enableTimer = data.get('enableTimer')
    if category == 0:
        category = None
    productLink = data.get('productLink', '')
    productTitle = data.get('productTitle', '')
    thumbnail_path = data.get('thumbnail', '')
    is_draft = data.get('isDraft', False)  # 新增参数：是否保存为草稿

    videos_per_day = data.get('videosPerDay')
    daily_times = data.get('dailyTimes')
    start_days = data.get('startDays')

    downloaded_files = []
    if file_urls:
        try:
            downloaded_files = download_video_urls(file_urls)
            # 注意：这里我们直接把下载得到的文件名加到 file_list 里
            file_list.extend(downloaded_files)
        except Exception as e:
            return jsonify({"code": 500, "msg": str(e), "data": None}), 500

    # 参数校验
    if not file_list:
        return jsonify({"code": 400, "msg": "文件列表不能为空", "data": None}), 400
    if not account_list:
        return jsonify({"code": 400, "msg": "账号列表不能为空", "data": None}), 400
    if not type:
        return jsonify({"code": 400, "msg": "平台类型不能为空", "data": None}), 400
    if not title:
        return jsonify({"code": 400, "msg": "标题不能为空", "data": None}), 400

    # 打印获取到的数据（仅作为示例）
    print("File List:", file_list)
    print("Account List:", account_list)

    try:
        match type:
            case 1:
                post_video_xhs(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days)
            case 2:
                post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days, is_draft)
            case 3:
                post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days, thumbnail_path, productLink, productTitle)
            case 4:
                post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days)
            case _:
                return jsonify({"code": 400, "msg": f"不支持的平台类型: {type}", "data": None}), 400

        # 返回响应给客户端
        return jsonify(
            {
                "code": 200,
                "msg": "发布任务已提交",
                "data": None
            }), 200
    except Exception as e:
        print(f"发布视频时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"发布失败: {str(e)}",
            "data": None
        }), 500
    finally:
        if downloaded_files:
            cleanup_downloaded_files(downloaded_files)


@publish_bp.route('/social/api/postVideoBatch', methods=['POST'])
def postVideoBatch():
    data_list = request.get_json()

    if not isinstance(data_list, list):
        return jsonify({"code": 400, "msg": "Expected a JSON array", "data": None}), 400
    for data in data_list:
        downloaded_files = []
        try:
            # 从JSON数据中提取fileList和accountList
            file_list = data.get('fileList', [])
            file_urls = data.get('fileUrls', [])
            account_list = data.get('accountList', [])
            type = data.get('type')
            title = data.get('title')
            tags = data.get('tags', [])
            category = data.get('category')
            enableTimer = data.get('enableTimer')
            if category == 0:
                category = None
            productLink = data.get('productLink', '')
            productTitle = data.get('productTitle', '')
            is_draft = data.get('isDraft', False)

            videos_per_day = data.get('videosPerDay')
            daily_times = data.get('dailyTimes')
            start_days = data.get('startDays')
            
            if file_urls:
                try:
                    downloaded_files = download_video_urls(file_urls)
                    # 注意：这里我们直接把下载得到的文件名加到 file_list 里
                    file_list.extend(downloaded_files)
                except Exception as e:
                    return jsonify({"code": 500, "msg": f"Failed to download urls for batch item: {e}", "data": None}), 500

            # 打印获取到的数据（仅作为示例）
            print("File List:", file_list)
            print("Account List:", account_list)
            match type:
                case 1:
                    post_video_xhs(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days)
                case 2:
                    post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                       start_days, is_draft)
                case 3:
                    post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                              start_days, productLink, productTitle)
                case 4:
                    post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                              start_days)
        finally:
            if downloaded_files:
                cleanup_downloaded_files(downloaded_files)
    # 返回响应给客户端
    return jsonify(
        {
            "code": 200,
            "msg": None,
            "data": None
        }), 200
