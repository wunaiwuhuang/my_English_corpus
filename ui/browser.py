"""
浏览器界面 - 查看和搜索Lemmas
"""
import streamlit as st
from services.lemma_service import lemma_service
from services.example_service import example_service
from services.relation_service import relation_service


def render():
    """渲染浏览器界面"""
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
    
    # 显示lemmas
    for lemma_data in lemmas:
        with st.container():
            # 标题行
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"## {lemma_data['lemma']}")
                if lemma_data['topic']:
                    st.caption(f"📚 Topic: {lemma_data['topic']}")
            
            with col2:
                # 删除按钮
                if st.button("🗑️ Delete", key=f"del_{lemma_data['id']}"):
                    success, msg = lemma_service.delete_lemma(lemma_data['lemma'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            # 基础信息
            col1, col2 = st.columns(2)
            
            with col1:
                if lemma_data['pronunciation_british']:
                    st.write(f"**Pronunciation:** /{lemma_data['pronunciation_british']}/")
                
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
            
            # Examples按钮
            examples = example_service.get_examples_by_lemma(lemma_data['lemma'])
            if examples:
                with st.expander(f"📖 Examples ({len(examples)})"):
                    for ex in examples:
                        st.write(f"• {ex['example']}")
                        # 显示关联的lemmas
                        lemma_tags = [f"**{l['lemma']}**" if l['is_valid'] 
                                    else f"~~{l['lemma']}~~" 
                                    for l in ex['lemmas']]
                        st.caption(f"Lemmas: {' | '.join(lemma_tags)}")
                        st.markdown("---")
            else:
                st.caption("_No examples yet_")
            
            # Relations按钮
            relations = relation_service.get_relations_by_lemma(lemma_data['lemma'])
            if relations:
                with st.expander(f"🔗 Relations ({len(relations)})"):
                    for rel in relations:
                        # 确定显示方向
                        if rel['lemma1'] == lemma_data['lemma']:
                            display = f"**{rel['lemma1']}** ({rel['specific_word1']}) ↔️ **{rel['lemma2']}** ({rel['specific_word2']})"
                        else:
                            display = f"**{rel['lemma2']}** ({rel['specific_word2']}) ↔️ **{rel['lemma1']}** ({rel['specific_word1']})"
                        
                        st.write(display)
                        st.caption(f"Type: {rel['relation_type']}")
                        if rel['note']:
                            st.caption(f"Note: {rel['note']}")
                        
                        # 显示网络图按钮
                        if st.button(f"🕸️ View Network", key=f"net_{rel['id']}"):
                            st.session_state['show_network'] = {
                                'lemma': lemma_data['lemma'],
                                'specific_word': rel['specific_word1'] if rel['lemma1'] == lemma_data['lemma'] else rel['specific_word2']
                            }
                        
                        st.markdown("---")
            else:
                st.caption("_No relations yet_")
            
            st.markdown("---")
    
    # 显示关系网络图（如果被触发）
    if 'show_network' in st.session_state:
        show_relation_network(
            st.session_state['show_network']['lemma'],
            st.session_state['show_network']['specific_word']
        )
        if st.button("❌ Close Network View"):
            del st.session_state['show_network']
            st.rerun()


def show_relation_network(lemma: str, specific_word: str):
    """显示关系网络图"""
    st.markdown("---")
    st.markdown(f"### 🕸️ Relation Network: {lemma} - {specific_word}")
    
    # 获取网络数据
    network_data = relation_service.get_relation_network(lemma, specific_word, max_depth=2)
    
    if not network_data['nodes']:
        st.info("No relations found for this lemma-word pair")
        return
    
    # 使用简单的文本展示（后续可以用Plotly/NetworkX绘图）
    st.write(f"**Nodes:** {len(network_data['nodes'])}")
    st.write(f"**Edges:** {len(network_data['edges'])}")
    
    # 显示节点
    with st.expander("📍 Nodes"):
        for node in network_data['nodes']:
            st.write(f"• {node['lemma']} - {node['word']}")
    
    # 显示边
    with st.expander("🔗 Connections"):
        for edge in network_data['edges']:
            st.write(f"• {edge['source']} → {edge['target']}")
            st.caption(f"  Type: {edge['type']}")
            if edge['note']:
                st.caption(f"  Note: {edge['note']}")