import os
import dash
from flask import request, send_from_directory

# 实例化应用
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    update_title=None,
    title="我的网盘空间",
)


@app.server.route("/upload", methods=["POST"])
def upload():
    """文件上传接口"""

    uploadId = request.values.get("uploadId")
    filename = request.files["file"].filename

    uploadId = "" if uploadId == "/" else uploadId

    try:
        os.mkdir(os.path.join("caches", uploadId))
    except FileExistsError:
        pass

    with open(os.path.join("caches", uploadId, filename), "wb") as f:
        for chunk in iter(lambda: request.files["file"].read(1024 * 1024 * 10), b""):
            f.write(chunk)

    return {"filename": filename}


@app.server.route("/download")
def download():
    """文件下载接口"""

    path = request.args.get("path")
    filename = request.args.get("filename")

    return send_from_directory(path, filename)
