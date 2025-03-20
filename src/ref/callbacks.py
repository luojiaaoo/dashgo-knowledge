import os
import dash
import uuid
import time
import shutil
from dash import set_props
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from dash.dependencies import Input, Output, State

from server import app

# 自定义工具函数
from utils import get_current_path, render_path_content


@app.callback(
    Output("current-path-files", "children"), Input("path-indicator", "items")
)
def render_files_list_by_items_change(items):
    """当前路径指示器items更新 -> 触发文件列表更新"""

    return render_path_content(items)


@app.callback(
    [
        Output("upload-file-modal", "visible"),
        Output("upload-file-modal", "children"),
    ],
    Input("open-upload-file-modal", "nClicks"),
    State("path-indicator", "items"),
    prevent_initial_call=True,
)
def open_upload_file_modal(nClicks, items):
    """控制打开文件上传模态框，以及模态框内上传组件的渲染"""

    # 获取当前目标路径
    current_path = get_current_path(items)

    return [
        True,
        fac.AntdDraggerUpload(
            id="upload-files",
            apiUrl="/upload",
            # 借助uploadId配合自定义文件上传接口简化文件上传控制过程
            uploadId=current_path or "/",
            text="文件上传",
            hint="点击或拖拽文件到此区域上传",
            multiple=True,
            showUploadList=False,
        ),
    ]


@app.callback(
    Output("current-path-files", "children", allow_duplicate=True),
    Input("upload-files", "lastUploadTaskRecord"),
    State("path-indicator", "items"),
    prevent_initial_call=True,
)
def render_files_list_by_files_upload(lastUploadTaskRecord, items):
    """每次文件上传成功后，更新文件列表"""

    if lastUploadTaskRecord:
        # 自动关闭模态框
        set_props("upload-file-modal", {"visible": False})

        # 更新文件列表
        return render_path_content(items)

    return dash.no_update


@app.callback(
    [
        Output("create-folder-modal", "visible"),
        Output("create-folder-modal", "children"),
    ],
    Input("open-create-folder-modal", "nClicks"),
    prevent_initial_call=True,
)
def open_create_folder_modal(nClicks):
    """控制打开新建文件夹模态框，以及模态框内输入框的渲染"""

    return [
        True,
        fac.AntdInput(
            id="create-folder-input",
            placeholder="请输入新文件夹名称",
            autoComplete="off",
            style=style(width="100%"),
        ),
    ]


@app.callback(
    Input("create-folder-modal", "okCounts"),
    [State("create-folder-input", "value"), State("path-indicator", "items")],
)
def create_folder(nClicks, folder_name, items):
    """处理新建文件夹操作"""

    # 若新文件夹名称不为空
    if folder_name:
        # 获取当前所在路径
        current_path = get_current_path(items)

        try:
            # 新建目标文件夹
            os.mkdir(os.path.join("caches", current_path, folder_name))

            # 消息提示
            set_props(
                "global-message",
                {"children": fac.AntdMessage(type="success", content="文件夹创建成功")},
            )

            # 更新文件列表
            set_props("current-path-files", {"children": render_path_content(items)})

            # 自动关闭模态框
            set_props("create-folder-modal", {"visible": False})

        except FileExistsError:
            # 若要创建的文件夹已存在
            # 消息提示
            set_props(
                "global-message",
                {"children": fac.AntdMessage(type="error", content="已存在同名文件夹")},
            )

    # 若新文件夹名称为空
    else:
        # 消息提示
        set_props(
            "global-message",
            {"children": fac.AntdMessage(type="error", content="文件夹名不能为空")},
        )


@app.callback(
    Input("current-path-files-table", "nClicksButton"),
    [
        State("current-path-files-table", "clickedContent"),
        State("current-path-files-table", "recentlyButtonClickedDataIndex"),
        State("current-path-files-table", "recentlyButtonClickedRow"),
        State("path-indicator", "items"),
    ],
)
def handle_files_table_operations(
    nClicksButton,
    clickedContent,
    recentlyButtonClickedDataIndex,
    recentlybuttonClickedRow,
    items,
):
    """处理文件列表中相关按钮操作"""

    # 处理进入指定文件夹操作
    if recentlyButtonClickedDataIndex == "文件/文件夹名":
        # 若点击的是文件夹
        if recentlybuttonClickedRow["custom"]["是否为文件夹"]:
            # 更新当前路径指示器
            new_items = [
                *items,
                {
                    "title": recentlybuttonClickedRow["custom"]["文件/文件夹名"],
                    # 针对非根目录的文件夹，添加唯一识别id，以便点击切换层级判断使用
                    "key": str(uuid.uuid4()),
                },
            ]

            # 更新当前路径指示器的items
            set_props("path-indicator", {"items": new_items})

    # 处理单文件下载操作
    elif clickedContent == "下载":
        # 模拟js针对单文件的直接下载
        set_props(
            "global-download",
            {
                "jsString": """
// 模拟下载指定文件
let downloadTarget = document.createElement('a')
downloadTarget.href = "{}"
downloadTarget.download = "{}"
document.body.appendChild(downloadTarget)
downloadTarget.click()
downloadTarget.remove()
""".format(
                    "/download?path={}&filename={}".format(
                        os.path.join(
                            "caches", recentlybuttonClickedRow["custom"]["所在路径"]
                        ),
                        recentlybuttonClickedRow["custom"]["文件/文件夹名"],
                    ),
                    recentlybuttonClickedRow["custom"]["文件/文件夹名"],
                )
            },
        )

    # 处理单文件/文件夹删除操作
    elif clickedContent == "删除":
        # 生成目标文件路径
        target_file_path = os.path.join(
            "caches",
            recentlybuttonClickedRow["custom"]["所在路径"],
            recentlybuttonClickedRow["custom"]["文件/文件夹名"],
        )

        # 若目标为文件夹
        if os.path.isdir(target_file_path):
            # 执行对目标文件夹的删除操作
            shutil.rmtree(target_file_path)

        else:
            # 执行对目标文件的删除操作
            os.remove(
                os.path.join(
                    "caches",
                    recentlybuttonClickedRow["custom"]["所在路径"],
                    recentlybuttonClickedRow["custom"]["文件/文件夹名"],
                )
            )

        # 更新文件列表
        set_props("current-path-files", {"children": render_path_content(items)})

        # 消息提示
        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    content="“%s”删除成功"
                    % recentlybuttonClickedRow["custom"]["文件/文件夹名"],
                    type="success",
                )
            },
        )


@app.callback(Input("path-indicator", "clickedItem"), State("path-indicator", "items"))
def switch_level(clickedItem, items):
    """处理当前路径指示器的点击层级切换"""

    # 若当前点击项不为根目录
    if clickedItem.get("itemKey"):
        # 提取当前点击项及之前所有项
        end_index = [
            i
            for i, item in enumerate(items)
            if item.get("key") == clickedItem["itemKey"]
        ][0]

        # 截断生成新的items
        new_items = items[: end_index + 1]

    # 若当前点击项为根目录
    else:
        new_items = items[:1]

    # 更新当前路径指示器
    set_props("path-indicator", {"items": new_items})


@app.callback(
    Input("download-files", "nClicks"),
    State("current-path-files-table", "selectedRows"),
    State("temp-uuids", "data"),
)
def handle_download_files(nClicks, selectedRows, origin_temp_uuids):
    """处理文件打包下载操作"""

    # 增加一点计算耗时^_^
    time.sleep(0.5)

    # 若未选择有效文件/文件夹记录
    if not selectedRows:
        # 消息提示
        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    type="warning", content="请先选择要下载的文件/文件夹"
                )
            },
        )

    # 若选择有效文件/文件夹记录
    else:
        # 将涉及的文件全部复制到临时路径下
        temp_uuid = str(uuid.uuid4())
        temp_path = os.path.join("temp", temp_uuid)
        os.mkdir(temp_path)

        for row in selectedRows:
            if row["custom"]["是否为文件夹"]:
                shutil.copytree(
                    os.path.join(
                        "caches",
                        row["custom"]["所在路径"],
                        row["custom"]["文件/文件夹名"],
                    ),
                    os.path.join(temp_path, row["custom"]["文件/文件夹名"]),
                )
            else:
                shutil.copy(
                    os.path.join(
                        "caches",
                        row["custom"]["所在路径"],
                        row["custom"]["文件/文件夹名"],
                    ),
                    os.path.join(temp_path, row["custom"]["文件/文件夹名"]),
                )

        # 打包临时压缩文件
        shutil.make_archive(
            os.path.join("temp", "打包下载_" + temp_uuid), "zip", temp_path
        )

        # 模拟针对单文件的直接下载
        set_props(
            "global-download",
            {
                "jsString": """
// 模拟下载指定文件
let downloadTarget = document.createElement('a')
downloadTarget.href = "{}"
downloadTarget.download = "{}"
document.body.appendChild(downloadTarget)
downloadTarget.click()
downloadTarget.remove()
""".format(
                    "/download?path={}&filename={}".format(
                        "temp",
                        "打包下载_" + temp_uuid + ".zip",
                    ),
                    "打包下载_" + temp_uuid + ".zip",
                )
            },
        )

        # 追加临时文件uuid
        set_props("temp-uuids", {"data": [*origin_temp_uuids, temp_uuid]})

    # 还原按钮状态
    set_props("download-files", {"loading": False})


@app.callback(Input("listen-app-unload", "unloaded"), State("temp-uuids", "data"))
def handle_temp_files_delete(unloaded, temp_uuids):
    """检测用户关闭或刷新页面后，打扫战场，清理先前产生的临时文件/文件夹"""

    for temp_uuid in temp_uuids:
        # 删除文件夹
        shutil.rmtree(os.path.join("temp", temp_uuid))
        # 删除压缩包
        os.remove(os.path.join("temp", "打包下载_" + temp_uuid + ".zip"))
