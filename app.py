# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Did you hear about the mathematician who was afraid of negative numbers? He'd stop at nothing to avoid them.","Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call a fake noodle? An impasta.",
    "Why did the bicycle fall over? Because it was two-tired!",
    "How do you organize a space party? You planet!",
    "What's orange and sounds like a parrot? A carrot.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "What do you call a fish with no eyes? Fsh.",
    "Parallel lines have so much in common. It’s a shame they’ll never meet.",
    "My dog used to chase people on a bike. It got so bad, we had to take his bike away.",
    "What do you call a boomerang that won't come back? A stick.",
    "Why did the coffee file a police report? It got mugged.",
    "What do you call a sad strawberry? A blueberry.",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "Why did the stadium get hot after the game? Because all the fans left.",
    "What do you call cheese that isn't yours? Nacho cheese.",
    "What's a vampire's favorite fruit? A neck-tarine.",
    "I only know 25 letters of the alphabet. I don't know Y.",
    "Did you hear about the restaurant on the moon? Great food, no atmosphere."
]

@app.route('/api/joke', methods=['GET'])
def get_joke():
    return jsonify({"joke": random.choice(jokes)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)