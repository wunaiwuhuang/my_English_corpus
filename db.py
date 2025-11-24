# db.py
import json
import os
from utils import new_uuid

# Data file paths
LEMMA_FILE = "data/lemmas.json"
EXAMPLE_FILE = "data/examples.json"
RELATION_FILE = "data/relations.json"

def load_data(file_path, default_value):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        save_data(file_path, default_value)
        return default_value

def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_lemmas():
    return load_data(LEMMA_FILE, [])

def get_all_examples():
    return load_data(EXAMPLE_FILE, [])

def get_all_relations():
    return load_data(RELATION_FILE, [])

def search_lemmas_by_topic(topic):
    lemmas = get_all_lemmas()
    return [l for l in lemmas if topic.lower() in l.get('topic', '').lower()]

def get_examples_by_lemma(lemma):
    examples = get_all_examples()
    result = []
    for ex in examples:
        if lemma in ex.get('lemmas', []):
            result.append(ex['text'])
    return result

def get_relations_by_lemma(lemma):
    relations = get_all_relations()
    result = []
    for r in relations:
        if r['lemma1'] == lemma or r['lemma2'] == lemma:
            result.append(r)
    return result

def get_all_topics():
    lemmas = get_all_lemmas()
    topics = {}
    for l in lemmas:
        topic = l.get('topic', 'Uncategorized')
        topics[topic] = topics.get(topic, 0) + 1
    return topics

def add_lemma(data):
    lemmas = get_all_lemmas()
    for l in lemmas:
        if l['lemma'] == data['lemma']:
            raise ValueError(f"Lemma '{data['lemma']}' already exists")
    lemmas.append(data)
    save_data(LEMMA_FILE, lemmas)

def add_example(text, lemmas_list):
    examples = get_all_examples()
    example_id = new_uuid()
    example_data = {
        'id': example_id,
        'text': text,
        'lemmas': lemmas_list
    }
    examples.append(example_data)
    save_data(EXAMPLE_FILE, examples)

def add_relation(lemma1, word1, lemma2, word2, rel_type, note):
    lemmas = get_all_lemmas()
    lemma_names = [l['lemma'] for l in lemmas]
    if lemma1 not in lemma_names:
        raise ValueError(f"Lemma1 '{lemma1}' does not exist")
    if lemma2 not in lemma_names:
        raise ValueError(f"Lemma2 '{lemma2}' does not exist")
    
    relations = get_all_relations()
    relation_data = {
        'id': new_uuid(),
        'lemma1': lemma1,
        'word1': word1,
        'lemma2': lemma2,
        'word2': word2,
        'relation_type': rel_type,
        'note': note
    }
    relations.append(relation_data)
    save_data(RELATION_FILE, relations)

def check_and_load_sample_data():
    os.makedirs("data", exist_ok=True)
    lemmas = load_data(LEMMA_FILE, [])
    if not lemmas:
        # Preload sample data
        sample_lemmas = [
            {
                'id': new_uuid(),
                'lemma': 'run',
                'pronunciation_br': '/rʌn/',
                'spell_nuance': '',
                'pos_meaning': {
                    'verb': ['to move quickly on foot', 'to operate a machine'],
                    'noun': ['an act of running', 'a continuous period of success']
                },
                'inflection': {'verb': ['ran', 'run']},
                'derivation': {'runner': 'a person who runs'},
                'common_collocation': 'run a business, run fast',
                'topic': 'movement'
            },
            {
                'id': new_uuid(),
                'lemma': 'child',
                'pronunciation_br': '/tʃaɪld/',
                'spell_nuance': '',
                'pos_meaning': {'noun': ['a young human being below the age of puberty']},
                'inflection': {'noun': ['children']},
                'derivation': {'childhood': 'the state of being a child'},
                'common_collocation': 'school child, only child',
                'topic': 'family'
            },
            {
                'id': new_uuid(),
                'lemma': 'good',
                'pronunciation_br': '/ɡʊd/',
                'spell_nuance': '',
                'pos_meaning': {
                    'adjective': ['to be of high quality', 'morally right'],
                    'noun': ['benefit or advantage']
                },
                'inflection': {},
                'derivation': {'goodness': 'the quality of being good'},
                'common_collocation': 'good idea, good luck',
                'topic': 'evaluation'
            },
            {
                'id': new_uuid(),
                'lemma': 'write',
                'pronunciation_br': '/raɪt/',
                'spell_nuance': '',
                'pos_meaning': {'verb': ['to mark letters or symbols on a surface']},
                'inflection': {'verb': ['wrote', 'written']},
                'derivation': {'writer': 'a person who writes'},
                'common_collocation': 'write a letter, write down',
                'topic': 'communication'
            },
            {
                'id': new_uuid(),
                'lemma': 'go',
                'pronunciation_br': '/ɡəʊ/',
                'spell_nuance': '',
                'pos_meaning': {'verb': ['to move from one place to another']},
                'inflection': {'verb': ['went', 'gone']},
                'derivation': {'goer': 'a frequent attendee'},
                'common_collocation': 'go home, go crazy',
                'topic': 'movement'
            }
        ]
        
        sample_examples = [
            {'id': new_uuid(), 'text': "She likes to run in the park.", 'lemmas': ['run']},
            {'id': new_uuid(), 'text': "He ran a successful company.", 'lemmas': ['run']},
            {'id': new_uuid(), 'text': "Children love playing outside.", 'lemmas': ['child']},
            {'id': new_uuid(), 'text': "That's a good point.", 'lemmas': ['good']},
            {'id': new_uuid(), 'text': "I need to write an email.", 'lemmas': ['write']},
            {'id': new_uuid(), 'text': "Let's go to the cinema!", 'lemmas': ['go']}
        ]
        
        sample_relations = [
            {
                'id': new_uuid(),
                'lemma1': 'run',
                'word1': 'ran',
                'lemma2': 'go',
                'word2': 'went',
                'relation_type': 'contextual_synonym',
                'note': 'Both past tense of movement verbs'
            },
            {
                'id': new_uuid(),
                'lemma1': 'child',
                'word1': 'children',
                'lemma2': 'good',
                'word2': 'goods',
                'relation_type': 'homograph',
                'note': 'Different meanings'
            }
        ]
        
        save_data(LEMMA_FILE, sample_lemmas)
        save_data(EXAMPLE_FILE, sample_examples)
        save_data(RELATION_FILE, sample_relations)
