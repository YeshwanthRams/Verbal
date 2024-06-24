from flask import Flask, render_template, jsonify, request
import json
import random
import os

app = Flask(__name__)

# Load the words and their meanings from the JSON file
with open('meanings.json') as f:
    words = json.load(f)

# Load the examples from the JSON file
with open('examples.json') as f:
    examples = json.load(f)

# Load or initialize the quiz stats
quiz_stats_file = 'quiz_stats.json'
if os.path.exists(quiz_stats_file):
    with open(quiz_stats_file) as f:
        quiz_stats = json.load(f)
else:
    quiz_stats = {word: {"correct": 0, "wrong": 0} for word in words}

@app.route('/')
def index():
    return render_template('index.html', words=words)

@app.route('/reveal/<word>')
def reveal(word):
    meaning = words.get(word)
    return jsonify(meaning=meaning)

@app.route('/examples/<word>')
def get_examples(word):
    example = examples.get(word)
    return jsonify(example=example)

@app.route('/quiz')
def quiz():
    word_list = list(words.keys())
    question_word = random.choice(word_list)
    correct_meaning = words[question_word]
    options = [correct_meaning]
    
    while len(options) < 4:
        random_word = random.choice(word_list)
        random_meaning = words[random_word]
        if random_meaning not in options:
            options.append(random_meaning)
    
    random.shuffle(options)
    
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
            quiz_stats[word]['correct'] += 1
        else:
            quiz_stats[word]['wrong'] += 1
        
        # Save updated stats to file
        with open(quiz_stats_file, 'w') as f:
            json.dump(quiz_stats, f)
    
    return jsonify({
        'is_correct': is_correct,
        'correct_meaning': correct_meaning,
        'example': example,
        'stats': quiz_stats[word]
    })

if __name__ == '__main__':
    app.run(debug=True)