from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from server import app
from dash.dependencies import Input, Output, State
import dash

# 构造应用初始化内容
app.layout = lambda: fuc.FefferyTopProgress(
    [
        # 全局消息提示
        fac.Fragment(id="global-message"),
        # 全局重定向
        fac.Fragment(id="global-redirect"),
        # 全局页面重载
        fac.Fragment(id="global-reload"),
        # 根节点url监听
        fuc.FefferyLocation(id="root-url"),
        # 应用根容器
        html.Div(
            id="root-container",
        ),
    ],
    listenPropsMode="include",
    includeProps=["root-container.children"],
    minimum=0.33,
    color="#1677ff",
)


@app.callback(
    Output("root-container", "children"),
    Input("root-url", "pathname"),
    State("root-url", "trigger"),
    prevent_initial_call=True,
)
def root_router(pathname, trigger):
    """根节点路由控制"""

    # 只允许第一次加载时触发
    if trigger != "load":
        return dash.no_update

    # 无需校验登录状态的公共页面
    if pathname == "/":
        from dash_view import index

        return index.render()

    # 处理核心功能页面渲染
    from dash_view import rag_page

    return rag_page.render(current_pathname=pathname)


if __name__ == "__main__":
    app.run(port=50000, debug=True)
