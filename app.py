from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

# Load the words and their meanings from the JSON file
with open('words.json') as f:
    words = json.load(f)

# Load the examples from the JSON file
with open('examples.json') as f:
    examples = json.load(f)

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

if __name__ == '__main__':
    app.run()
