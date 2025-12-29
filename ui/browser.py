"""
浏览器界面 - 查看和搜索Lemmas
"""
import streamlit as st
from services.lemma_service import lemma_service
from services.example_service import example_service
from services.relation_service import relation_service
import config


def render():
    """渲染浏览器界面"""
    
    # 自定义CSS - 压缩行高和间距
    st.markdown("""
        <style>
        /* 压缩容器间距 */
        .element-container {
            margin-bottom: 0px !important;
        }
        
        /* 压缩按钮高度 */
        .stButton button {
            padding: 0.1rem 0.4rem !important;
            font-size: 0.9rem !important;
            height: 0.5rem !important;
        }
        
        /* 压缩文本行高 */
        .stMarkdown p {
            margin-bottom: 0.3rem !important;
            line-height: 1.3 !important;
        }
        
        /* 压缩分隔线间距 */
        hr {
            margin-top: 0.05rem !important;
            margin-bottom: 0.05rem !important;
        }
        
        /* 压缩列之间的间距 */
        [data-testid="column"] {
            padding: 0.2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔍 Browse Dictionary")
    
    # 统计面板
    col1, col2, col3 = st.columns(3)
    
    total_lemmas = lemma_service.count_lemmas()
    topics = lemma_service.get_all_topics()
    
    with col1:
        st.metric("Total Lemmas", total_lemmas)
    with col2:
        st.metric("Topics", len(topics))
    with col3:
        # 计算有examples的lemmas数量
        all_lemmas = lemma_service.get_all_lemmas()
        lemmas_with_examples = sum(1 for l in all_lemmas 
                                   if example_service.get_examples_by_lemma(l['lemma']))
        st.metric("Lemmas with Examples", lemmas_with_examples)
    
    st.markdown("---")
    
    # 搜索和过滤
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_term = st.text_input("🔎 Search lemma", placeholder="Type to search...")
    
    with col2:
        selected_topic = st.selectbox(
            "📚 Filter by Topic",
            ["All Topics"] + topics
        )
    
    with col3:
        sort_by = st.selectbox(
            "🔤 Sort by",
            ["Alphabetical", "Recently Added", "Topic"]
        )
    
    # 获取lemmas
    if search_term:
        lemmas = lemma_service.search_lemmas(search_term)
    elif selected_topic != "All Topics":
        lemmas = lemma_service.get_lemmas_by_topic(selected_topic)
    else:
        sort_map = {
            "Alphabetical": "lemma",
            "Recently Added": "created_at",
            "Topic": "topic"
        }
        lemmas = lemma_service.get_all_lemmas(sort_by=sort_map[sort_by])
    
    # 显示结果
    st.markdown(f"### Found {len(lemmas)} lemma(s)")
    
    if not lemmas:
        st.info("No lemmas found. Try a different search or add some lemmas!")
        return
    
    # 显示lemmas（超紧凑模式）
    for lemma_data in lemmas:
        with st.container():
            # 超紧凑显示：一行展示所有操作
            col1, col2, col3, col4, col5 = st.columns([8, 0.7, 0.7, 0.7, 0.7])
            
            with col1:
                # 构建显示文本
                lemma_display = f"**{lemma_data['lemma']}**"
                if lemma_data['pronunciation_british']:
                    lemma_display += f" /{lemma_data['pronunciation_british']}/"
                if lemma_data['topic']:
                    lemma_display += f" · 📚 {lemma_data['topic']}"
                st.markdown(lemma_display)
            
            with col2:
                # 展开按钮 - 修改key避免冲突
                if st.button("👁️", key=f"view_btn_{lemma_data['id']}", help="View details"):
                    expand_key = f"expanded_{lemma_data['id']}"
                    st.session_state[expand_key] = not st.session_state.get(expand_key, False)
            
            with col3:
                # 编辑按钮
                if st.button("✏️", key=f"edit_btn_{lemma_data['id']}", help="Edit"):
                    st.session_state[f'editing_lemma_{lemma_data["id"]}'] = True
                    # 初始化POS编辑数据
                    if lemma_data['pos_meaning']:
                        st.session_state[f'edit_pos_{lemma_data["id"]}'] = lemma_data['pos_meaning'].copy()
                    else:
                        st.session_state[f'edit_pos_{lemma_data["id"]}'] = [{'pos': 'n.', 'meanings': ['']}]
            
            with col4:
                # 删除按钮
                if st.button("🗑️", key=f"del_btn_{lemma_data['id']}", help="Delete"):
                    success, msg = lemma_service.delete_lemma(lemma_data['lemma'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col5:
                # 关系网络按钮（如果有relations）
                relations = relation_service.get_relations_by_lemma(lemma_data['lemma'])
                if relations:
                    if st.button("🕸️", key=f"net_btn_{lemma_data['id']}", help="Relation network"):
                        net_key = f'show_network_{lemma_data["id"]}'
                        st.session_state[net_key] = not st.session_state.get(net_key, False)
            
            # 展开查看详细内容
            if st.session_state.get(f"expanded_{lemma_data['id']}", False):
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if lemma_data['spell_nuance']:
                        st.write(f"**Spell Nuance:** {lemma_data['spell_nuance']}")
                    
                    # POS和meanings
                    if lemma_data['pos_meaning']:
                        st.write("**Meanings:**")
                        for pm in lemma_data['pos_meaning']:
                            st.write(f"*{pm['pos']}*")
                            for i, meaning in enumerate(pm['meanings'], 1):
                                st.write(f"  {i}. {meaning}")
                
                with col2:
                    # Inflection
                    if lemma_data['inflection']:
                        st.write("**Inflection:**")
                        for key, values in lemma_data['inflection'].items():
                            st.write(f"  *{key}:* {', '.join(values)}")
                    
                    # Derivation
                    if lemma_data['derivation']:
                        st.write("**Derivation:**")
                        for deriv in lemma_data['derivation']:
                            if deriv.get('meaning'):
                                st.write(f"  • {deriv['word']}: {deriv['meaning']}")
                            else:
                                st.write(f"  • {deriv['word']}")
                    
                    # Collocation
                    if lemma_data['collocation']:
                        st.write(f"**Collocation:** {lemma_data['collocation']}")
                
                st.markdown("---")
                
                # Examples按钮
                examples = example_service.get_examples_by_lemma(lemma_data['lemma'])
                if examples:
                    if st.button(f"📖 Examples ({len(examples)})", key=f"show_ex_{lemma_data['id']}"):
                        ex_key = f'show_examples_{lemma_data["id"]}'
                        st.session_state[ex_key] = not st.session_state.get(ex_key, False)
                    
                    if st.session_state.get(f'show_examples_{lemma_data["id"]}', False):
                        for ex in examples:
                            st.write(f"• {ex['example']}")
                            lemma_tags = [f"**{l['lemma']}**" if l['is_valid'] 
                                        else f"~~{l['lemma']}~~" 
                                        for l in ex['lemmas']]
                            st.caption(f"Lemmas: {' | '.join(lemma_tags)}")
                            st.markdown("---")
                else:
                    st.caption("_No examples yet_")
                
                # Relations列表
                relations = relation_service.get_relations_by_lemma(lemma_data['lemma'])
                if relations:
                    if st.button(f"🔗 Relations ({len(relations)})", key=f"show_rel_{lemma_data['id']}"):
                        rel_key = f'show_relations_{lemma_data["id"]}'
                        st.session_state[rel_key] = not st.session_state.get(rel_key, False)
                    
                    if st.session_state.get(f'show_relations_{lemma_data["id"]}', False):
                        for rel in relations:
                            if rel['lemma1'] == lemma_data['lemma']:
                                display = f"**{rel['lemma1']}** ({rel['specific_word1']}) ↔️ **{rel['lemma2']}** ({rel['specific_word2']})"
                            else:
                                display = f"**{rel['lemma2']}** ({rel['specific_word2']}) ↔️ **{rel['lemma1']}** ({rel['specific_word1']})"
                            
                            st.write(display)
                            st.caption(f"Type: {rel['relation_type']}")
                            if rel['note']:
                                st.caption(f"Note: {rel['note']}")
                            st.markdown("---")
                else:
                    st.caption("_No relations yet_")
            
            # 显示关系网络（如果被触发，显示在当前lemma下方）
            if st.session_state.get(f'show_network_{lemma_data["id"]}', False):
                st.markdown("---")
                show_relation_network_inline(lemma_data, relations)
            
            # 编辑表单（在下方显示）
            if st.session_state.get(f'editing_lemma_{lemma_data["id"]}', False):
                render_edit_form(lemma_data)
            
            st.markdown("---")


def show_relation_network_inline(lemma_data, relations):
    """在当前位置显示关系网络图（去重）"""
    st.markdown(f"##### 🕸️ Relation Network")
    
    # 获取第一个relation的specific word
    first_rel = relations[0]
    lemma = lemma_data['lemma']
    specific_word = first_rel['specific_word1'] if first_rel['lemma1'] == lemma else first_rel['specific_word2']
    
    # 获取网络数据
    network_data = relation_service.get_relation_network(lemma, specific_word, max_depth=2)
    
    if not network_data['nodes']:
        st.info("No relations found")
        return
    
    st.write(f"**Starting from:** {lemma} - {specific_word}")
    
    # 去重边（只保留一个方向）
    seen_edges = set()
    unique_edges = []
    
    for edge in network_data['edges']:
        # 创建标准化的边ID（小的在前）
        source = edge['source']
        target = edge['target']
        
        # 按字母顺序排序，确保 A-B 和 B-A 会有相同的ID
        edge_id = tuple(sorted([source, target]))
        
        if edge_id not in seen_edges:
            seen_edges.add(edge_id)
            # 确保当前lemma在前面
            if source.startswith(lemma):
                unique_edges.append(edge)
            else:
                # 交换方向，让当前lemma在前
                unique_edges.append({
                    'source': target,
                    'target': source,
                    'type': edge['type'],
                    'note': edge['note']
                })
    
    st.write(f"**Nodes:** {len(network_data['nodes'])} | **Connections:** {len(unique_edges)}")
    
    # 显示连接（去重后）
    st.markdown("**Network Map:**")
    for edge in unique_edges:
        source_parts = edge['source'].split('-')
        target_parts = edge['target'].split('-')
        
        st.write(f"• **{source_parts[0]}** `{source_parts[1]}` → **{target_parts[0]}** `{target_parts[1]}`")
        st.caption(f"  ↳ {edge['type']}" + (f" | {edge['note']}" if edge['note'] else ""))
    
    # 显示所有节点
    with st.expander("📍 All Nodes", expanded=False):
        cols = st.columns(3)
        for i, node in enumerate(network_data['nodes']):
            with cols[i % 3]:
                st.write(f"• **{node['lemma']}**")
                st.caption(f"  `{node['word']}`")


def render_edit_form(lemma_data):
    """渲染编辑表单"""
    st.markdown("---")
    st.markdown(f"#### ✏️ Edit Lemma: {lemma_data['lemma']}")
    
    # POS管理（在表单外）
    st.markdown("##### Part of Speech & Meanings")
    
    # 获取或初始化POS编辑数据
    pos_key = f'edit_pos_{lemma_data["id"]}'
    if pos_key not in st.session_state:
        if lemma_data['pos_meaning']:
            st.session_state[pos_key] = lemma_data['pos_meaning'].copy()
        else:
            st.session_state[pos_key] = [{'pos': 'n.', 'meanings': ['']}]
    
    # 显示所有POS
    for i, pos_item in enumerate(st.session_state[pos_key]):
        col1, col2, col3 = st.columns([2, 7, 1])
        
        with col1:
            new_pos = st.selectbox(
                "POS",
                config.POS_OPTIONS,
                key=f"edit_pos_select_{lemma_data['id']}_{i}",
                index=config.POS_OPTIONS.index(pos_item['pos']) if pos_item['pos'] in config.POS_OPTIONS else 0,
                label_visibility="collapsed"
            )
            st.session_state[pos_key][i]['pos'] = new_pos
        
        with col2:
            meanings_text = st.text_area(
                "Meanings",
                value='\n'.join(pos_item['meanings']) if pos_item['meanings'] else '',
                key=f"edit_meanings_{lemma_data['id']}_{i}",
                height=100,
                placeholder="One meaning per line",
                label_visibility="collapsed"
            )
            st.session_state[pos_key][i]['meanings'] = [
                m.strip() for m in meanings_text.split('\n') if m.strip()
            ]
        
        with col3:
            if st.button("❌", key=f"edit_remove_pos_{lemma_data['id']}_{i}", help="Remove"):
                if len(st.session_state[pos_key]) > 1:
                    st.session_state[pos_key].pop(i)
                    st.rerun()
                else:
                    st.warning("At least one POS required")
    
    # 添加新POS
    if st.button("➕ Add POS", key=f"edit_add_pos_{lemma_data['id']}"):
        st.session_state[pos_key].append({'pos': 'n.', 'meanings': ['']})
        st.rerun()
    
    st.markdown("---")
    
    # 其他字段表单
    with st.form(f"edit_lemma_form_{lemma_data['id']}"):
        st.markdown("##### Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_pronunciation = st.text_input(
                "Pronunciation (British)",
                value=lemma_data['pronunciation_british'] or ""
            )
            new_spell_nuance = st.text_input(
                "Spell Nuance",
                value=lemma_data['spell_nuance'] or ""
            )
        
        with col2:
            new_collocation = st.text_area(
                "Collocation",
                value=lemma_data['collocation'] or "",
                height=100
            )
            new_topic = st.text_input(
                "Topic",
                value=lemma_data['topic'] or ""
            )
        
        st.markdown("##### Inflection")
        # 将inflection转换为文本格式
        inflection_text = ""
        if lemma_data['inflection']:
            inflection_parts = []
            for key, values in lemma_data['inflection'].items():
                inflection_parts.append(f"{key}: {', '.join(values)}")
            inflection_text = " | ".join(inflection_parts)
        
        new_inflection = st.text_area(
            "Inflection",
            value=inflection_text,
            help="Format: verb: past, past_participle | noun: plural",
            height=80
        )
        
        st.markdown("##### Derivation")
        # 将derivation转换为文本格式
        derivation_text = ""
        if lemma_data['derivation']:
            derivation_lines = []
            for deriv in lemma_data['derivation']:
                if deriv.get('meaning'):
                    derivation_lines.append(f"{deriv['word']}: {deriv['meaning']}")
                else:
                    derivation_lines.append(deriv['word'])
            derivation_text = '\n'.join(derivation_lines)
        
        new_derivation = st.text_area(
            "Derivation",
            value=derivation_text,
            help="Format: word1:meaning1 (one per line)",
            height=80
        )
        
        # 提交按钮
        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("💾 Save All Changes", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save:
            # 验证POS meanings
            pos_meaning_data = []
            for item in st.session_state[pos_key]:
                if item['meanings']:
                    pos_meaning_data.append({
                        'pos': item['pos'],
                        'meanings': item['meanings']
                    })
            
            if not pos_meaning_data:
                st.error("At least one POS with meanings is required")
                return
            
            # 解析inflection
            inflection_data = None
            if new_inflection.strip():
                inflection_data = {}
                for line in new_inflection.split('|'):
                    line = line.strip()
                    if ':' in line:
                        key, values = line.split(':', 1)
                        inflection_data[key.strip()] = [v.strip() for v in values.split(',')]
            
            # 解析derivation
            derivation_data = []
            if new_derivation.strip():
                for line in new_derivation.split('\n'):
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
            
            # 更新lemma
            success, msg = lemma_service.update_lemma(
                lemma_data['lemma'],
                pronunciation_british=new_pronunciation.strip() or None,
                spell_nuance=new_spell_nuance.strip() or None,
                pos_meaning=pos_meaning_data,
                inflection=inflection_data,
                derivation=derivation_data if derivation_data else None,
                collocation=new_collocation.strip() or None,
                topic=new_topic.strip() or None
            )
            
            if success:
                st.success(msg)
                # 清理session state
                del st.session_state[f'editing_lemma_{lemma_data["id"]}']
                if pos_key in st.session_state:
                    del st.session_state[pos_key]
                st.rerun()
            else:
                st.error(msg)
        
        if cancel:
            # 清理session state
            del st.session_state[f'editing_lemma_{lemma_data["id"]}']
            if pos_key in st.session_state:
                del st.session_state[pos_key]
            st.rerun()