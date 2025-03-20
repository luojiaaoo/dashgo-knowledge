from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style

from server import app

# 自动注册回调函数
import callbacks  # noqa: F401

# 构造相关操作模态框
modals = fac.Fragment(
    [
        # 上传文件操作模态框
        fac.AntdModal(id="upload-file-modal", title="上传文件", mask=False),
        # 新建文件夹操作模态框
        fac.AntdModal(
            id="create-folder-modal",
            title="新建文件夹",
            mask=False,
            okClickClose=False,
            renderFooter=True,
        ),
    ]
)

# 构造应用初始化内容
app.layout = html.Div(
    [
        # 手动控制favicon
        fuc.FefferySetFavicon(favicon="/assets/logo.svg"),
        # 全局消息提示
        fac.Fragment(id="global-message"),
        # 全局文件下载跳转
        fuc.FefferyExecuteJs(id="global-download"),
        # 记录当前应用生命周期内产生的临时文件uuid数组
        dcc.Store(id="temp-uuids", data=[]),
        # 监听当前应用重载或关闭事件
        fuc.FefferyListenUnload(id="listen-app-unload"),
        # 模态框
        modals,
        # 页首
        fac.AntdCenter(
            fac.AntdSpace(
                [
                    html.Img(src="/assets/logo.svg", height=64),
                    fac.AntdText(
                        "我的云盘空间",
                        style=style(
                            fontSize=36,
                            fontFamily="Microsoft YaHei",
                        ),
                    ),
                ]
            )
        ),
        # 操作区
        html.Div(
            [
                # 顶部操作区
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            # 当前路径指示器，可点击交互
                            fac.AntdBreadcrumb(
                                id="path-indicator", items=[{"title": "全部文件"}]
                            )
                        ),
                        fac.AntdCol(
                            # 操作按钮
                            fac.AntdSpace(
                                [
                                    fac.AntdButton(
                                        "上传文件",
                                        id="open-upload-file-modal",
                                        icon=fac.AntdIcon(icon="antd-plus"),
                                        type="primary",
                                    ),
                                    fac.AntdButton(
                                        "新建文件夹",
                                        id="open-create-folder-modal",
                                        icon=fac.AntdIcon(icon="antd-folder-add"),
                                    ),
                                    fac.AntdTooltip(
                                        fac.AntdButton(
                                            "下载文件",
                                            id="download-files",
                                            icon=fac.AntdIcon(icon="antd-download"),
                                            autoSpin=True,
                                            loadingChildren="处理中",
                                        ),
                                        title="打包下载已选中文件/文件夹",
                                    ),
                                ]
                            )
                        ),
                    ],
                    justify="space-between",
                ),
                fac.AntdDivider(),
                # 文件列表渲染区
                html.Div(id="current-path-files"),
            ],
            style=style(
                background="white",
                borderRadius="20px 20px 0 0",
                minHeight="calc(100vh - 68px)",
                padding="40px 24px",
                boxSizing="border-box",
            ),
        ),
    ],
    style=style(
        background="#f5f6f8", paddingLeft=56, paddingRight=56, minHeight="100vh"
    ),
)

if __name__ == "__main__":
    app.run(debug=False)  # 设置debug=True，开启开发调试模式
