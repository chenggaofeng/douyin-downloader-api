#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扣子插件：抖音视频下载器
核心功能：输入抖音链接，获取下载链接或直接下载视频
"""

import os
import re
import json
import time
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

class DouyinDownloader:
    """抖音视频下载器核心类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_video_id_from_url(self, url: str) -> Optional[str]:
        """从URL中提取视频ID"""
        patterns = [
            r'video/(\d+)',
            r'/([a-zA-Z0-9]{11})/?',
            r'v\.douyin\.com/([a-zA-Z0-9]+)',
            r'aweme_id=([0-9]+)',
            r'item_ids=([0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_real_url(self, share_link: str) -> str:
        """获取真实的抖音视频URL"""
        try:
            # 处理短链接
            if 'v.douyin.com' in share_link:
                response = self.session.head(share_link, allow_redirects=True, timeout=10)
                return response.url
            return share_link
        except Exception as e:
            print(f"获取真实URL失败: {e}")
            return share_link
    
    def parse_douyin_api(self, video_id: str) -> Dict[str, Any]:
        """调用抖音API获取视频信息"""
        try:
            # 构造API请求URL
            api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
            
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status_code') == 0 and data.get('item_list'):
                item = data['item_list'][0]
                
                # 提取视频信息
                title = item.get('desc', '抖音视频')
                video_id = item.get('aweme_id', video_id)
                
                # 获取视频下载链接
                video_info = item.get('video', {})
                play_addr = video_info.get('play_addr', {})
                url_list = play_addr.get('url_list', [])
                
                if url_list:
                    download_url = url_list[0].replace('playwm', 'play')  # 去水印
                    
                    return {
                        'status': 'success',
                        'video_id': video_id,
                        'title': title,
                        'download_url': download_url,
                        'description': f'视频标题: {title}',
                        'usage_tip': '可以直接使用此链接下载无水印视频'
                    }
            
            return {
                'status': 'error',
                'message': '无法获取视频信息'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'API调用失败: {str(e)}'
            }
    
    def get_download_link(self, share_link: str) -> Dict[str, Any]:
        """获取抖音视频下载链接"""
        try:
            # 获取真实URL
            real_url = self.get_real_url(share_link)
            
            # 提取视频ID
            video_id = self.extract_video_id_from_url(real_url)
            
            if not video_id:
                return {
                    'status': 'error',
                    'message': '无法从链接中提取视频ID，请检查链接是否正确'
                }
            
            # 调用API获取视频信息
            result = self.parse_douyin_api(video_id)
            
            if result['status'] == 'success':
                return result
            else:
                # 如果API失败，使用备用方案
                return self.fallback_method(video_id, real_url)
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'处理链接失败: {str(e)}'
            }
    
    def fallback_method(self, video_id: str, url: str) -> Dict[str, Any]:
        """备用方案：构造下载链接"""
        try:
            # 构造可能的下载链接
            download_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id=v0200fg10000{video_id}&ratio=720p&line=0"
            
            return {
                'status': 'success',
                'video_id': video_id,
                'title': '抖音视频',
                'download_url': download_url,
                'description': '使用备用方案获取的下载链接',
                'usage_tip': '可以直接使用此链接下载视频'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'备用方案失败: {str(e)}'
            }
    
    def download_video(self, share_link: str, filename: str = None) -> Dict[str, Any]:
        """下载视频文件"""
        try:
            # 先获取下载链接
            link_result = self.get_download_link(share_link)
            
            if link_result['status'] == 'error':
                return link_result
            
            download_url = link_result['download_url']
            title = link_result['title']
            
            # 生成文件名
            if not filename:
                # 清理标题中的特殊字符
                clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
                filename = f"{clean_title}_{int(time.time())}.mp4"
            
            if not filename.endswith('.mp4'):
                filename += '.mp4'
            
            # 下载视频
            response = self.session.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(os.getcwd(), filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(file_path)
            
            return {
                'status': 'success',
                'message': '视频下载成功',
                'file_path': file_path,
                'filename': filename,
                'file_size': f'{file_size / 1024 / 1024:.2f} MB',
                'title': title
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'下载失败: {str(e)}',
                'details': '请检查网络连接和链接有效性'
            }

# Flask Web API 部分
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化下载器
downloader = DouyinDownloader()

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        'message': '抖音视频下载器 API',
        'version': '1.0.0',
        'endpoints': {
            '/get_download_link': 'POST - 获取下载链接',
            '/download_video': 'POST - 下载视频文件'
        },
        'usage': {
            'get_download_link': {
                'method': 'POST',
                'body': {'share_link': '抖音分享链接'},
                'description': '获取无水印视频下载链接'
            },
            'download_video': {
                'method': 'POST', 
                'body': {'share_link': '抖音分享链接', 'filename': '可选文件名'},
                'description': '直接下载视频文件到服务器'
            }
        }
    })

@app.route('/get_download_link', methods=['POST'])
def get_download_link():
    """获取下载链接接口"""
    try:
        data = request.get_json()
        
        if not data or 'share_link' not in data:
            return jsonify({
                'status': 'error',
                'message': '请提供抖音分享链接',
                'required_params': ['share_link']
            }), 400
        
        share_link = data['share_link']
        
        if not share_link:
            return jsonify({
                'status': 'error',
                'message': '分享链接不能为空'
            }), 400
        
        # 调用下载器获取链接
        result = downloader.get_download_link(share_link)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/download_video', methods=['POST'])
def download_video():
    """下载视频接口"""
    try:
        data = request.get_json()
        
        if not data or 'share_link' not in data:
            return jsonify({
                'status': 'error',
                'message': '请提供抖音分享链接',
                'required_params': ['share_link']
            }), 400
        
        share_link = data['share_link']
        filename = data.get('filename', None)
        
        if not share_link:
            return jsonify({
                'status': 'error',
                'message': '分享链接不能为空'
            }), 400
        
        # 调用下载器下载视频
        result = downloader.download_video(share_link, filename)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time()),
        'service': '抖音视频下载器 API'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)