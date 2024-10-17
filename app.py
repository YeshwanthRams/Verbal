from flask import Flask, render_template, jsonify, request
import json
import random
import os

app = Flask(__name__)

with open('groups.json') as f:
    word_groups = json.load(f)

with open('examples.json') as f:
    examples = json.load(f)

words = {}
for group_words in word_groups.values():
    words.update(group_words)

quiz_stats_file = 'stats.json'
if os.path.exists(quiz_stats_file):
    with open(quiz_stats_file) as f:
        stats = json.load(f)
else:
    stats = {word: {"correct": 0, "wrong": 0} for word in words}

@app.route('/')
def index():
    return render_template('index.html', words=words, stats=stats, group_count=len(word_groups))

@app.route('/reveal/<word>')
def reveal(word):
    meaning = words.get(word)
    return jsonify(meaning=meaning)

@app.route('/examples/<word>')
def get_examples(word):
    example = examples.get(word)
    return jsonify(example=example)

word_usage_counts = {word: 0 for word in words}

@app.route('/quiz')
def quiz():
    start_group = int(request.args.get('start', 1))
    end_group = int(request.args.get('end', len(word_groups)))

    if start_group > end_group:
        start_group, end_group = end_group, start_group

    group_names = list(word_groups.keys())

    selected_groups = group_names[start_group - 1:end_group]

    selected_words = {}
    for group in selected_groups:
        selected_words.update(word_groups[group])

    word_list = list(selected_words.keys())

    if not word_list:
        return jsonify({})

    min_usage_count = min(word_usage_counts.get(word, 0) for word in word_list)
    least_used_words = [word for word in word_list if word_usage_counts.get(word, 0) == min_usage_count]

    question_word = random.choice(least_used_words)
    correct_meaning = selected_words[question_word]
    options = [correct_meaning]

    all_meanings = list(selected_words.values())
    all_meanings.remove(correct_meaning)
    wrong_options = random.sample(all_meanings, min(3, len(all_meanings)))

    options.extend(wrong_options)
    random.shuffle(options)

    word_usage_counts[question_word] += 1

    return jsonify({
        'word': question_word,
        'options': options,
        'correct_index': options.index(correct_meaning)
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    word = data['word']
    selected_index = data['selectedIndex']
    correct_index = data['correctIndex']
    is_first_try = data['isFirstTry']

    is_correct = selected_index == correct_index
    correct_meaning = words[word]
    example = examples.get(word, "No example available.")

    if is_first_try:
        if is_correct:
            stats[word]['correct'] += 1
        else:
            stats[word]['wrong'] += 1

        with open('stats.json', 'w') as f:
            json.dump(stats, f)

    return jsonify({
        'is_correct': is_correct,
        'correct_meaning': correct_meaning,
        'example': example,
        'stats': stats[word]
    })

if __name__ == '__main__':
    app.run(debug=True)
