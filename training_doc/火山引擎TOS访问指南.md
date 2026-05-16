# 火山引擎 TOS 访问指南

## 连接信息

| 配置项 | 值 |
|--------|-----|
| Endpoint | `tos-cn-beijing.volces.com` |
| Region | `cn-beijing` |
| Bucket | `drama-flow` |
| 域名 | `drama-flow.tos-cn-beijing.volces.com` |
| Access Key | `<YOUR_ACCESS_KEY>` |
| Secret Key | `<YOUR_SECRET_KEY>` |

## 存储内容

Bucket 中存放了一批短视频 Demo 素材，共 18 个文件：

```
videos/andu_chencang/andu_chencang_00.mp4       108.69 MB
videos/andu_chencang/andu_chencang_00_cover.jpg   0.12 MB
videos/andu_chencang/andu_chencang_01.mp4       108.01 MB
videos/andu_chencang/andu_chencang_01_cover.jpg   0.08 MB
videos/andu_chencang/andu_chencang_02.mp4       112.09 MB
videos/andu_chencang/andu_chencang_02_cover.jpg   0.09 MB
videos/andu_chencang/andu_chencang_03.mp4       102.99 MB
videos/andu_chencang/andu_chencang_03_cover.jpg   0.08 MB
videos/andu_chencang/andu_chencang_04.mp4       111.10 MB
videos/andu_chencang/andu_chencang_04_cover.jpg   0.07 MB
videos/andu_chencang/andu_chencang_05.mp4       108.18 MB
videos/andu_chencang/andu_chencang_05_cover.jpg   0.09 MB
videos/andu_chencang/andu_chencang_06.mp4       111.27 MB
videos/andu_chencang/andu_chencang_06_cover.jpg   0.10 MB
videos/andu_chencang/andu_chencang_07.mp4       109.36 MB
videos/andu_chencang/andu_chencang_07_cover.jpg   0.08 MB
videos/andu_chencang/andu_chencang_08.mp4        81.39 MB
videos/andu_chencang/andu_chencang_08_cover.jpg   0.10 MB
```

- `_00` ~ `_08` 共 9 个视频片段（每段约 1 分钟）
- 每个视频对应一张 `_cover.jpg` 封面图

---

## 封面图 — 公开 URL 直接访问

封面图允许公开读取，直接拼接 URL 即可：

```
https://drama-flow.tos-cn-beijing.volces.com/videos/andu_chencang/andu_chencang_00_cover.jpg
https://drama-flow.tos-cn-beijing.volces.com/videos/andu_chencang/andu_chencang_01_cover.jpg
...
https://drama-flow.tos-cn-beijing.volces.com/videos/andu_chencang/andu_chencang_08_cover.jpg
```

浏览器可以直接打开，无需任何认证。

---

## 视频 — 通过 TOS SDK 下载

视频文件不公开，需使用火山引擎 TOS SDK 的 `get_object` 接口下载。

### 1. 安装依赖

```bash
pip install tos
```

### 2. 完整可运行代码

以下代码可直接运行：列出所有文件、下载封面（直接 HTTP）、下载视频（通过 SDK）。

```python
"""
访问火山引擎 TOS Bucket 中的 Demo 视频素材。
- 封面图：公开 URL，直接 HTTP GET
- 视频：通过 TOS SDK get_object 下载
"""
import os
from tos import TosClientV2

# ========== 连接信息 ==========
ACCESS_KEY = "<YOUR_ACCESS_KEY>"
SECRET_KEY = "<YOUR_SECRET_KEY>"
ENDPOINT = "tos-cn-beijing.volces.com"
REGION = "cn-beijing"
BUCKET = "drama-flow"
DOMAIN = f"https://{BUCKET}.{ENDPOINT}"

# 前缀（目录）
PREFIX = "videos/andu_chencang/"
# 共 9 个片段
INDICES = list(range(9))  # 0 ~ 8


def get_client():
    """创建 TOS 客户端"""
    return TosClientV2(ACCESS_KEY, SECRET_KEY, ENDPOINT, REGION)


def list_all_files(client):
    """列出 Bucket 中所有文件"""
    result = client.list_objects(BUCKET, prefix=PREFIX, max_keys=50)
    for obj in result.contents:
        size_mb = obj.size / 1024 / 1024
        print(f"  {obj.key}  ({size_mb:.2f} MB)")


def get_cover_url(index: int) -> str:
    """拼接封面图公开 URL"""
    return f"{DOMAIN}/{PREFIX}andu_chencang_{index:02d}_cover.jpg"


def get_video_key(index: int) -> str:
    """拼接视频的对象 Key"""
    return f"{PREFIX}andu_chencang_{index:02d}.mp4"


def download_cover(index: int, output_dir: str = "./downloads"):
    """通过 HTTP 直接下载封面图"""
    import urllib.request

    os.makedirs(output_dir, exist_ok=True)
    url = get_cover_url(index)
    filename = f"andu_chencang_{index:02d}_cover.jpg"
    filepath = os.path.join(output_dir, filename)

    print(f"  下载封面: {url}")
    urllib.request.urlretrieve(url, filepath)
    print(f"  -> {filepath}")


def download_video(client, index: int, output_dir: str = "./downloads"):
    """通过 SDK get_object 下载视频"""
    os.makedirs(output_dir, exist_ok=True)
    key = get_video_key(index)
    filename = f"andu_chencang_{index:02d}.mp4"
    filepath = os.path.join(output_dir, filename)

    print(f"  下载视频: {key}")
    # 先查大小
    head = client.head_object(BUCKET, key)
    total = int(head.content_length) if head.content_length else 0
    print(f"  文件大小: {total / 1024 / 1024:.2f} MB")

    # 流式下载
    resp = client.get_object(BUCKET, key)
    with open(filepath, "wb") as f:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            f.write(chunk)
    print(f"  -> {filepath}")


def download_all(output_dir: str = "./downloads"):
    """下载全部封面和视频"""
    client = get_client()

    for i in INDICES:
        download_cover(i, output_dir)
        download_video(client, i, output_dir)

    print(f"\n全部下载完成，共 {len(INDICES) * 2} 个文件 -> {os.path.abspath(output_dir)}")


# ========== 使用示例 ==========
if __name__ == "__main__":
    client = get_client()

    # 1. 列出所有文件
    print("=== Bucket 文件列表 ===")
    list_all_files(client)

    # 2. 获取某张封面的 URL
    print(f"\n封面 00: {get_cover_url(0)}")

    # 3. 下载全部内容
    # download_all("./downloads")
```

### 3. 运行

```bash
pip install tos
python access_demo.py
```

---

