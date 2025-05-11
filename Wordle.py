from flask import Flask, render_template, request, redirect, session, url_for
from random import choice
from words import word_list

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session handling

SQUARES = {
    'correct_place': '🟩',
    'correct_letter': '🟨',
    'incorrect_letter': '⬛'
}

ALLOWED_GUESSES = 6

def correct_place(letter):
    return f"<span class='correct'>{letter}</span>"

def correct_letter(letter):
    return f"<span class='present'>{letter}</span>"

def incorrect_letter(letter):
    return f"<span class='absent'>{letter}</span>"

def check_guess(guess, answer):
    guessed = []
    wordle_pattern = []
    key_colors = {}

    for i, letter in enumerate(guess):
        if answer[i] == guess[i]:
            guessed.append(correct_place(letter))
            wordle_pattern.append(SQUARES['correct_place'])
            key_colors[letter] = 'correct'
        elif letter in answer:
            guessed.append(correct_letter(letter))
            wordle_pattern.append(SQUARES['correct_letter'])
            if key_colors.get(letter) != 'correct':
                key_colors[letter] = 'present'
        else:
            guessed.append(incorrect_letter(letter))
            wordle_pattern.append(SQUARES['incorrect_letter'])
            if key_colors.get(letter) not in ['correct', 'present']:
                key_colors[letter] = 'absent'

    return ''.join(guessed), ''.join(wordle_pattern), key_colors

@app.route('/name', methods=['GET', 'POST'])
def name():
    if request.method == 'POST':
        name = request.form.get('username', '').strip()
        if name:
            session['player'] = name
            return redirect(url_for('index'))
    return render_template('name.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'player' not in session:
        return redirect(url_for('name'))

    if 'answer' not in session:
        session['answer'] = choice(word_list)
        session['guesses'] = []
        session['patterns'] = []
        session['keyboard'] = {}
        session['won'] = None

    if request.method == 'POST':
        guess = request.form.get('guess', '').upper().strip()
        previous_words = [g.get('raw', ''.join(filter(str.isalpha, g['word']))) for g in session['guesses']]

        if len(guess) != 5:
            session['message'] = 'Your guess must be exactly 5 letters.'
        elif guess in previous_words:
            session['message'] = 'You already guessed that word!'
        elif guess not in word_list:
            session['message'] = 'That word is not in the word list.'
        else:
            guessed, pattern, key_colors = check_guess(guess, session['answer'])

            for key, value in key_colors.items():
                current = session['keyboard'].get(key)
                if current == 'correct':
                    continue
                if current == 'present' and value == 'absent':
                    continue
                session['keyboard'][key] = value

            session['guesses'].append({
                'word': guessed,
                'raw': guess
                })

            session['patterns'].append(pattern)

            if guess == session['answer']:
                session['won'] = True
            elif len(session['guesses']) == ALLOWED_GUESSES:
                session['won'] = False

            session.modified = True

        return redirect(url_for('index'))

    return render_template(
        'index.html',
        guesses=session.get('guesses', []),
        won=session.get('won'),
        answer=session.get('answer') if session.get('won') is not None else None,
        keyboard=session.get('keyboard', {}),
        message=session.pop('message', None)
    )

@app.route('/reset')
def reset():
    player = session.get('player')
    
    session.pop('answer', None)
    session.pop('guesses', None)
    session.pop('patterns', None)
    session.pop('keyboard', None)
    session.pop('won', None)
    session.pop('message', None)

    session['player'] = player

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
