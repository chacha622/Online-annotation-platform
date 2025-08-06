# ✅ 主程序入口：Streamlit 标注平台
try:
    import streamlit as st
    from annotation_access_control import check_user_role, has_export_permission
    from assignment_manager import get_user_tasks
    from dataset_loader import load_all_user_task_data, task_data_upload_ui
    from task_manager import task_admin_ui
    from task_guard import guard_user_task_access
except ModuleNotFoundError:
    import sys
    sys.exit("❌ 缺少必要模块 'streamlit'，请先运行：pip install streamlit pandas openpyxl xlsxwriter")

st.set_page_config(page_title="标注平台", layout="wide")

# 登录并获取角色
user_name, user_role = check_user_role()
is_owner = user_role == "发布人"

st.title("📌 多任务标注平台")

# 发布人页面
if is_owner:
    st.header("🧩 发布人操作区")
    task_data_upload_ui()     # 上传任务数据
    task_admin_ui()           # 管理任务（改名、删除、分配）
    st.divider()
    st.header("🗂️ 标注区（支持自我标注）")
    all_tasks = list(st.session_state.all_assignments.keys())
    task_to_mark = st.selectbox("选择任务开始标注", all_tasks)
    df_dict = load_all_user_task_data(user_name, [task_to_mark])
else:
    st.header("🗂️ 我的任务")
    assigned = get_user_tasks(user_name)
    valid_tasks = guard_user_task_access(user_name, assigned)
    if not valid_tasks:
        st.stop()
    task_to_mark = st.selectbox("选择任务开始标注", valid_tasks)
    df_dict = load_all_user_task_data(user_name, [task_to_mark])

# 标注主入口
if task_to_mark and task_to_mark in df_dict:
    df = df_dict[task_to_mark]
    st.session_state.data = df
    st.session_state.step = 3  # 强制标注页
    from streamlit_annotation_tool_v2 import annotation_page, export_results
    annotation_page()
    if st.session_state.export_allowed:
        export_results()
else:
    st.warning("请选择任务并确保数据已成功加载。")
