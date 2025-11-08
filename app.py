"""
主应用入口文件
运行: streamlit run app.py
"""
import streamlit as st
import config

# 导入UI模块
from ui import browser, add_lemma, add_example, add_relation


def main():
    """主函数"""
    # 页面配置
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 侧边栏导航
    with st.sidebar:
        st.title(f"{config.PAGE_ICON} Dictionary")
        st.markdown("---")
        
        # 导航菜单
        page = st.radio(
            "Navigation",
            ["🔍 Browse", "📝 Add Lemma", "📖 Add Example", "🔗 Add Relation"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 显示统计信息
        from services.lemma_service import lemma_service
        
        st.markdown("### 📊 Statistics")
        total = lemma_service.count_lemmas()
        topics = lemma_service.get_all_topics()
        
        st.metric("Total Lemmas", total)
        st.metric("Topics", len(topics))
        
        st.markdown("---")
        st.caption("English Dictionary Warehouse v1.0")
        st.caption("Built with Streamlit & SQLite")
    
    # 路由到对应页面
    if page == "🔍 Browse":
        browser.render()
    elif page == "📝 Add Lemma":
        add_lemma.render()
    elif page == "📖 Add Example":
        add_example.render()
    elif page == "🔗 Add Relation":
        add_relation.render()


if __name__ == "__main__":
    main()