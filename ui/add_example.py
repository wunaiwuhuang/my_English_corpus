"""
添加Example界面 (Sheet 2)
"""
import streamlit as st
from services.example_service import example_service
from services.lemma_service import lemma_service


def render():
    """渲染添加Example界面"""
    st.title("📝 Add Example")
    st.markdown("---")
    
    # 添加新example表单
    with st.form("add_example_form", clear_on_submit=True):
        example_text = st.text_area(
            "Example Sentence *",
            height=100,
            help="Enter an example sentence"
        )
        
        lemmas_input = st.text_input(
            "Linked Lemmas",
            help="Enter lemmas separated by commas. Valid lemmas will be shown in green, invalid in gray."
        )
        
        # 实时验证lemmas
        if lemmas_input:
            lemmas_list = [l.strip().lower() for l in lemmas_input.split(',') if l.strip()]
            
            st.write("**Lemma Validation:**")
            cols = st.columns(min(len(lemmas_list), 4))
            
            for i, lemma in enumerate(lemmas_list):
                col_idx = i % 4
                with cols[col_idx]:
                    if lemma_service.lemma_exists(lemma):
                        st.success(f"✅ {lemma}")
                    else:
                        st.warning(f"⚠️ {lemma} (not found)")
        
        # 提交按钮
        col1, col2 = st.columns([1, 5])
        with col1:
            submit = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
    
    # 处理提交
    if submit:
        if not example_text.strip():
            st.error("Example不能为空")
            return
        
        lemmas_list = []
        if lemmas_input:
            lemmas_list = [l.strip().lower() for l in lemmas_input.split(',') if l.strip()]
        
        # 创建example
        success, message, example_id = example_service.create_example(
            example=example_text,
            lemmas=lemmas_list
        )
        
        if success:
            st.success(f"✅ {message}")
            
            # 显示创建的example信息
            example_data = example_service.get_example(example_id)
            if example_data:
                with st.expander("📖 Created Example", expanded=True):
                    st.write(example_data['example'])
                    st.write("**Linked Lemmas:**")
                    for l in example_data['lemmas']:
                        if l['is_valid']:
                            st.success(f"✅ {l['lemma']}")
                        else:
                            st.warning(f"⚠️ {l['lemma']} (lemma not found, will link automatically when added)")
        else:
            st.error(f"❌ {message}")
    
    # 显示所有examples
    st.markdown("---")
    st.markdown("### 📋 All Examples")
    
    examples = example_service.get_all_examples()
    
    if not examples:
        st.info("No examples added yet")
        return
    
    # 搜索框
    search = st.text_input("🔎 Search examples", placeholder="Type to search...")
    
    # 过滤examples
    if search:
        filtered_examples = [e for e in examples if search.lower() in e['example'].lower()]
    else:
        filtered_examples = examples
    
    st.write(f"Showing {len(filtered_examples)} example(s)")
    
    # 显示examples
    for ex in filtered_examples:
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.write(f"**{ex['example']}**")
                
                # 显示关联的lemmas
                if ex['lemmas']:
                    lemma_badges = []
                    for l in ex['lemmas']:
                        if l['is_valid']:
                            lemma_badges.append(f"**{l['lemma']}**")
                        else:
                            lemma_badges.append(f"~~{l['lemma']}~~ _(not found)_")
                    st.caption(f"Lemmas: {' | '.join(lemma_badges)}")
                else:
                    st.caption("_No linked lemmas_")
            
            with col2:
                # 编辑按钮
                if st.button("✏️", key=f"edit_{ex['id']}"):
                    st.session_state[f'editing_{ex["id"]}'] = True
                
                # 删除按钮
                if st.button("🗑️", key=f"del_{ex['id']}"):
                    success, msg = example_service.delete_example(ex['id'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            # 编辑表单
            if st.session_state.get(f'editing_{ex["id"]}', False):
                with st.form(f"edit_form_{ex['id']}"):
                    new_example = st.text_area("Example", value=ex['example'])
                    
                    current_lemmas = ', '.join([l['lemma'] for l in ex['lemmas']])
                    new_lemmas = st.text_input("Lemmas (comma-separated)", value=current_lemmas)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("💾 Save", use_container_width=True)
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if save:
                        lemmas_list = [l.strip().lower() for l in new_lemmas.split(',') if l.strip()]
                        success, msg = example_service.update_example(
                            ex['id'],
                            example=new_example,
                            lemmas=lemmas_list
                        )
                        if success:
                            st.success(msg)
                            del st.session_state[f'editing_{ex["id"]}']
                            st.rerun()
                        else:
                            st.error(msg)
                    
                    if cancel:
                        del st.session_state[f'editing_{ex["id"]}']
                        st.rerun()
            
            st.markdown("---")