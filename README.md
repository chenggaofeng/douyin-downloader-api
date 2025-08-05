# 抖音视频下载器 API

这是一个抖音视频下载器的API服务，可以获取无水印的抖音视频下载链接。

## 功能特性

- 🎬 获取抖音视频无水印下载链接
- 📱 支持短链接和完整链接
- 🔄 直接下载视频到本地
- 🛡️ 安全可靠的API接口

## API接口

### 1. 获取下载链接
```
POST /get_download_link
{
    "share_link": "https://v.douyin.com/M2IF10d0tOM/"
}
```

### 2. 下载视频
```
POST /download_video
{
    "share_link": "https://v.douyin.com/M2IF10d0tOM/",
    "filename": "我的抖音视频"
}
```

## 部署说明

### Vercel部署（推荐）
1. Fork此仓库
2. 在Vercel中导入项目
3. 自动部署完成

### Netlify部署
1. Fork此仓库
2. 在Netlify中导入项目
3. 自动部署完成

### Railway部署
1. Fork此仓库
2. 在Railway中导入项目
3. 自动部署完成

## 扣子插件配置

部署完成后，使用 `coze_github.yaml` 文件导入到扣子平台：
1. 将文件中的服务器地址替换为您的实际部署地址
2. 在扣子平台导入插件配置
3. 开始使用抖音视频下载功能

## 技术栈

- Python 3.9+
- FastAPI
- 抖音视频解析库

## 许可证

MIT License