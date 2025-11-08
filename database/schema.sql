-- Lemmas表 (Sheet 1)
CREATE TABLE IF NOT EXISTS lemmas (
    id TEXT PRIMARY KEY,
    lemma TEXT UNIQUE NOT NULL,
    pronunciation_british TEXT,
    spell_nuance TEXT,
    pos_meaning TEXT,           -- JSON格式: [{"pos": "n.", "meanings": ["意思1", "意思2"]}]
    inflection TEXT,            -- JSON格式: {"verb": ["past", "past_participle"], "noun": ["plural"]}
    derivation TEXT,            -- JSON格式: [{"word": "derived_word", "meaning": "特殊含义"}]
    collocation TEXT,
    topic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Examples表 (Sheet 2)
CREATE TABLE IF NOT EXISTS examples (
    id TEXT PRIMARY KEY,
    example TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example和Lemma的多对多关系
CREATE TABLE IF NOT EXISTS example_lemma_links (
    example_id TEXT NOT NULL,
    lemma TEXT NOT NULL,
    is_valid INTEGER DEFAULT 1,  -- 1表示lemma存在，0表示不存在（灰色显示）
    FOREIGN KEY (example_id) REFERENCES examples(id) ON DELETE CASCADE,
    FOREIGN KEY (lemma) REFERENCES lemmas(lemma) ON DELETE CASCADE,
    PRIMARY KEY (example_id, lemma)
);

-- Relations表 (Sheet 3)
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma1 TEXT NOT NULL,
    specific_word1 TEXT NOT NULL,
    lemma2 TEXT NOT NULL,
    specific_word2 TEXT NOT NULL,
    relation_type TEXT NOT NULL,  -- 'interchangeable' 或 'contextual_synonym'
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lemma1) REFERENCES lemmas(lemma) ON DELETE CASCADE,
    FOREIGN KEY (lemma2) REFERENCES lemmas(lemma) ON DELETE CASCADE,
    CHECK (relation_type IN ('interchangeable', 'contextual_synonym'))
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_lemmas_lemma ON lemmas(lemma);
CREATE INDEX IF NOT EXISTS idx_lemmas_topic ON lemmas(topic);
CREATE INDEX IF NOT EXISTS idx_example_lemma_links_lemma ON example_lemma_links(lemma);
CREATE INDEX IF NOT EXISTS idx_relations_lemma1 ON relations(lemma1, specific_word1);
CREATE INDEX IF NOT EXISTS idx_relations_lemma2 ON relations(lemma2, specific_word2);