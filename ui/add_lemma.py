"""
添加Lemma界面 (Sheet 1)
"""
import streamlit as st
from services.lemma_service import lemma_service
from services.example_service import example_service
from utils.validators import validate_lemma
import config


def render():
    """渲染添加Lemma界面"""
    st.title("📝 Add Lemma")
    st.markdown("---")
    
    # 初始化session state
    if 'pos_meanings' not in st.session_state:
        st.session_state.pos_meanings = [{'pos': 'n.', 'meanings': ['']}]
    
    # POS管理区域（在表单外）
    st.markdown("### Part of Speech & Meanings")
    st.caption("Configure POS and meanings before submitting")
    
    # 显示当前所有POS
    for i, pos_item in enumerate(st.session_state.pos_meanings):
        col1, col2, col3 = st.columns([2, 7, 1])
        
        with col1:
            new_pos = st.selectbox(
                "POS", 
                config.POS_OPTIONS, 
                key=f"pos_select_{i}",
                index=config.POS_OPTIONS.index(pos_item['pos']) if pos_item['pos'] in config.POS_OPTIONS else 0,
                label_visibility="collapsed"
            )
            st.session_state.pos_meanings[i]['pos'] = new_pos
        
        with col2:
            meanings_text = st.text_area(
                "Meanings", 
                value='\n'.join(pos_item['meanings']) if pos_item['meanings'] else '',
                key=f"meanings_area_{i}",
                height=100,
                placeholder="One meaning per line",
                label_visibility="collapsed"
            )
            st.session_state.pos_meanings[i]['meanings'] = [
                m.strip() for m in meanings_text.split('\n') if m.strip()
            ]
        
        with col3:
            if st.button("❌", key=f"remove_pos_btn_{i}", help="Remove this POS"):
                if len(st.session_state.pos_meanings) > 1:
                    st.session_state.pos_meanings.pop(i)
                    st.rerun()
                else:
                    st.warning("At least one POS is required")
    
    # 添加新POS按钮
    if st.button("➕ Add Another POS"):
        st.session_state.pos_meanings.append({'pos': 'n.', 'meanings': ['']})
        st.rerun()
    
    st.markdown("---")
    
    # 使用表单提交其他信息
    with st.form("add_lemma_form", clear_on_submit=True):
        st.markdown("### Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lemma_input = st.text_input(
                "Lemma *", 
                help="Space will be converted to underscore, only letters, ' and _ allowed"
            )
            pronunciation = st.text_input("Pronunciation (British)")
            spell_nuance = st.text_input(
                "Spell Nuance (Optional)", 
                help="British left, American right"
            )
        
        with col2:
            collocation = st.text_area("Collocation", height=100)
            topic = st.text_input("Topic (Optional)")
        
        st.markdown("### Inflection (Optional)")
        inflection_text = st.text_area(
            "Inflection",
            help="Format: verb: past, past_participle | noun: plural",
            height=80
        )
        
        st.markdown("### Derivation (Optional)")
        derivation_text = st.text_area(
            "Derivation",
            help="Format: word1:meaning1 (one per line)",
            height=80
        )
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🔄 Clear All", use_container_width=True)
    
    # 处理清空
    if clear:
        st.session_state.pos_meanings = [{'pos': 'n.', 'meanings': ['']}]
        st.rerun()
    
    # 处理提交
    if submit:
        if not lemma_input:
            st.error("Lemma不能为空")
            return
        
        # 验证lemma
        valid, formatted_lemma, error = validate_lemma(lemma_input)
        if not valid:
            st.error(error)
            return
        
        # 准备POS meanings
        pos_meaning_data = []
        for item in st.session_state.pos_meanings:
            if item['meanings']:
                pos_meaning_data.append({
                    'pos': item['pos'],
                    'meanings': item['meanings']
                })
        
        if not pos_meaning_data:
            st.error("至少需要添加一个POS和meaning")
            return
        
        # 解析inflection
        inflection_data = None
        if inflection_text.strip():
            inflection_data = {}
            for line in inflection_text.split('|'):
                line = line.strip()
                if ':' in line:
                    key, values = line.split(':', 1)
                    inflection_data[key.strip()] = [v.strip() for v in values.split(',')]
        
        # 解析derivation
        derivation_data = []
        if derivation_text.strip():
            for line in derivation_text.split('\n'):
                line = line.strip()
                if line:
                    if ':' in line:
                        word, meaning = line.split(':', 1)
                        derivation_data.append({
                            'word': word.strip(),
                            'meaning': meaning.strip()
                        })
                    else:
                        derivation_data.append({
                            'word': line,
                            'meaning': None
                        })
        
        # 创建lemma
        success, message, lemma_id = lemma_service.create_lemma(
            lemma=formatted_lemma,
            pronunciation_british=pronunciation.strip() if pronunciation else None,
            spell_nuance=spell_nuance.strip() if spell_nuance else None,
            pos_meaning=pos_meaning_data,
            inflection=inflection_data,
            derivation=derivation_data if derivation_data else None,
            collocation=collocation.strip() if collocation else None,
            topic=topic.strip() if topic else None
        )
        
        if success:
            st.success(f"✅ {message}")
            # 刷新example的有效性
            example_service.refresh_lemma_validity()
            # 重置POS meanings
            st.session_state.pos_meanings = [{'pos': 'n.', 'meanings': ['']}]
            st.rerun()
        else:
            st.error(f"❌ {message}")
    
    # 显示最近添加的lemmas
    st.markdown("---")
    st.markdown("### 📋 Recently Added")
    
    lemmas = lemma_service.get_all_lemmas(sort_by='created_at')
    if lemmas:
        recent = lemmas[:5]  # 显示最近5个
        for lemma_data in recent:
            with st.expander(f"**{lemma_data['lemma']}** - {lemma_data['topic'] or 'No topic'}"):
                st.write(f"**Pronunciation:** {lemma_data['pronunciation_british'] or 'N/A'}")
                if lemma_data['pos_meaning']:
                    st.write("**Meanings:**")
                    for pm in lemma_data['pos_meaning']:
                        st.write(f"- *{pm['pos']}* {', '.join(pm['meanings'])}")
    else:
        st.info("No lemmas added yet")