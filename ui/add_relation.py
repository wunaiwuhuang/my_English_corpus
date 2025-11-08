"""
添加Relation界面 (Sheet 3)
"""
import streamlit as st
from services.relation_service import relation_service
from services.lemma_service import lemma_service
import config


def render():
    """渲染添加Relation界面"""
    st.title("🔗 Add Relation")
    st.markdown("---")
    
    # 添加新relation表单
    with st.form("add_relation_form", clear_on_submit=True):
        st.markdown("### First Lemma")
        col1, col2 = st.columns(2)
        
        with col1:
            lemma1 = st.text_input("Lemma 1 *", help="Must exist in dictionary")
        with col2:
            specific_word1 = st.text_input("Specific Word 1 *", help="Single word only")
        
        # 验证lemma1
        if lemma1:
            lemma1_formatted = lemma1.strip().lower()
            if lemma_service.lemma_exists(lemma1_formatted):
                st.success(f"✅ '{lemma1_formatted}' found")
            else:
                st.error(f"❌ '{lemma1_formatted}' not found. Please add it first.")
        
        st.markdown("### Second Lemma")
        col1, col2 = st.columns(2)
        
        with col1:
            lemma2 = st.text_input("Lemma 2 *", help="Must exist in dictionary")
        with col2:
            specific_word2 = st.text_input("Specific Word 2 *", help="Single word only")
        
        # 验证lemma2
        if lemma2:
            lemma2_formatted = lemma2.strip().lower()
            if lemma_service.lemma_exists(lemma2_formatted):
                st.success(f"✅ '{lemma2_formatted}' found")
            else:
                st.error(f"❌ '{lemma2_formatted}' not found. Please add it first.")
        
        st.markdown("### Relation Details")
        relation_type = st.selectbox(
            "Relation Type *",
            config.RELATION_TYPES,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        note = st.text_area("Note (Optional)", height=100)
        
        # 提交按钮
        col1, col2 = st.columns([1, 5])
        with col1:
            submit = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
    
    # 处理提交
    if submit:
        if not all([lemma1, specific_word1, lemma2, specific_word2]):
            st.error("所有必填字段都必须填写")
            return
        
        # 创建relation
        success, message, relation_id = relation_service.create_relation(
            lemma1=lemma1.strip().lower(),
            specific_word1=specific_word1.strip().lower(),
            lemma2=lemma2.strip().lower(),
            specific_word2=specific_word2.strip().lower(),
            relation_type=relation_type,
            note=note.strip() if note else None
        )
        
        if success:
            st.success(f"✅ {message}")
            
            # 显示创建的relation
            rel_data = relation_service.get_relation(relation_id)
            if rel_data:
                with st.expander("🔗 Created Relation", expanded=True):
                    st.write(f"**{rel_data['lemma1']}** ({rel_data['specific_word1']}) ↔️ "
                           f"**{rel_data['lemma2']}** ({rel_data['specific_word2']})")
                    st.write(f"**Type:** {rel_data['relation_type']}")
                    if rel_data['note']:
                        st.write(f"**Note:** {rel_data['note']}")
        else:
            st.error(f"❌ {message}")
    
    # 显示所有relations
    st.markdown("---")
    st.markdown("### 📋 All Relations")
    
    relations = relation_service.get_all_relations()
    
    if not relations:
        st.info("No relations added yet")
        return
    
    # 过滤选项
    col1, col2 = st.columns(2)
    with col1:
        search_lemma = st.text_input("🔎 Filter by lemma", placeholder="Type to filter...")
    with col2:
        filter_type = st.selectbox(
            "Filter by type",
            ["All Types"] + config.RELATION_TYPES,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    # 过滤relations
    filtered_relations = relations
    
    if search_lemma:
        search_lower = search_lemma.lower()
        filtered_relations = [r for r in filtered_relations 
                            if search_lower in r['lemma1'] or search_lower in r['lemma2']]
    
    if filter_type != "All Types":
        filtered_relations = [r for r in filtered_relations if r['relation_type'] == filter_type]
    
    st.write(f"Showing {len(filtered_relations)} relation(s)")
    
    # 显示relations
    for rel in filtered_relations:
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.write(f"### {rel['lemma1']} ({rel['specific_word1']}) ↔️ {rel['lemma2']} ({rel['specific_word2']})")
                st.caption(f"**Type:** {rel['relation_type'].replace('_', ' ').title()}")
                if rel['note']:
                    st.write(f"**Note:** {rel['note']}")
                st.caption(f"_Created: {rel['created_at']}_")
            
            with col2:
                # 编辑按钮
                if st.button("✏️", key=f"edit_{rel['id']}"):
                    st.session_state[f'editing_rel_{rel["id"]}'] = True
                
                # 删除按钮
                if st.button("🗑️", key=f"del_{rel['id']}"):
                    success, msg = relation_service.delete_relation(rel['id'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            # 编辑表单
            if st.session_state.get(f'editing_rel_{rel["id"]}', False):
                with st.form(f"edit_form_{rel['id']}"):
                    st.markdown("##### Edit Relation")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_lemma1 = st.text_input("Lemma 1", value=rel['lemma1'])
                        new_word1 = st.text_input("Specific Word 1", value=rel['specific_word1'])
                    with col2:
                        new_lemma2 = st.text_input("Lemma 2", value=rel['lemma2'])
                        new_word2 = st.text_input("Specific Word 2", value=rel['specific_word2'])
                    
                    new_type = st.selectbox(
                        "Relation Type",
                        config.RELATION_TYPES,
                        index=config.RELATION_TYPES.index(rel['relation_type']),
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    new_note = st.text_area("Note", value=rel['note'] or "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("💾 Save", use_container_width=True)
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if save:
                        success, msg = relation_service.update_relation(
                            rel['id'],
                            lemma1=new_lemma1.strip().lower(),
                            specific_word1=new_word1.strip().lower(),
                            lemma2=new_lemma2.strip().lower(),
                            specific_word2=new_word2.strip().lower(),
                            relation_type=new_type,
                            note=new_note.strip() if new_note else None
                        )
                        if success:
                            st.success(msg)
                            del st.session_state[f'editing_rel_{rel["id"]}']
                            st.rerun()
                        else:
                            st.error(msg)
                    
                    if cancel:
                        del st.session_state[f'editing_rel_{rel["id"]}']
                        st.rerun()
            
            st.markdown("---")