import os
import uuid
from datetime import datetime
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


def get_current_path(items):
    """根据当前路径指示器items参数推导所在目录"""

    return "/".join([item["title"] for item in items[1:]])


def render_path_content(items):
    """基于当前路径指示器items生成文件列表"""

    # 获取目标路径
    current_path = get_current_path(items)

    # 获取目标路径下全部文件
    current_path_files = os.listdir(os.path.join("caches", current_path))

    # 空内容提示
    if not current_path_files:
        return fac.AntdCenter(
            fac.AntdEmpty(description="当前路径下还没有东西哦O_o~"),
            style=style(paddingTop=150),
        )

    # 基于AntdTable，基于当前路径下文件生成文件列表
    return fac.AntdTable(
        id="current-path-files-table",
        key=str(uuid.uuid4()),  # 强制刷新用
        columns=[
            {
                "dataIndex": "文件/文件夹名",
                "title": "文件/文件夹名",
                "renderOptions": {"renderType": "button"},
            },
            {"dataIndex": "修改时间", "title": "修改时间"},
            {
                "dataIndex": "操作",
                "title": "操作",
                "renderOptions": {"renderType": "button"},
            },
        ],
        # 默认优先将文件夹排在前面
        data=sorted(
            [
                {
                    "文件/文件夹名": (
                        {"type": "link", "content": file, "icon": "antd-folder"}
                        if os.path.isdir(os.path.join("caches", current_path, file))
                        else {"type": "text", "content": file}
                    ),
                    "修改时间": datetime.fromtimestamp(
                        os.path.getmtime(os.path.join("caches", current_path, file))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "操作": [
                        *(
                            []
                            if os.path.isdir(os.path.join("caches", current_path, file))
                            else [{"type": "link", "content": "下载"}]
                        ),
                        {"type": "link", "content": "删除", "danger": True},
                    ],
                    # 携带所需原始数据信息
                    "custom": {
                        "文件/文件夹名": file,
                        "所在路径": current_path,
                        "是否为文件夹": os.path.isdir(
                            os.path.join("caches", current_path, file)
                        ),
                    },
                }
                for file in current_path_files
            ],
            key=lambda item: item["custom"]["是否为文件夹"],
            reverse=True,
        ),
        sortOptions={
            "sortDataIndexes": ["文件/文件夹名", "修改时间"],
        },
        pagination=False,  # 关闭分页
        rowSelectionType="checkbox",  # 开启行多选功能
    )
