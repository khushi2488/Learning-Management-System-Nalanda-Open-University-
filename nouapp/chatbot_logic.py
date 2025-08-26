# nouapp/chatbot_logic.py
import json
import os
import random
import re
from django.conf import settings

class NalandaChatbot:
    def __init__(self):
        # Path to the FAQ data file
        data_path = os.path.join(settings.BASE_DIR, 'nouapp', 'static', 'data', 'faq_data.json')
        
        try:
            with open(data_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            # Default data if file doesn't exist
            self.data = [
                {
                    "tag": "greeting",
                    "patterns": ["hi", "hello", "hey", "is anyone there", "good day"],
                    "responses": ["Hello! Welcome to Nalanda Open University. How can I help you?", "Hi there! How can I assist you today?"]
                },
                {
                    "tag": "fallback",
                    "patterns": [],
                    "responses": ["I'm sorry, I don't have the answer to that yet. Please contact the admin office at admin@nalanda.edu.in for more information."]
                }
            ]

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        
        # Remove special characters and extra spaces
        user_input = re.sub(r'[^\w\s]', '', user_input)
        user_input = re.sub(r'\s+', ' ', user_input)
        
        # Check for exact matches first
        for intent in self.data:
            for pattern in intent['patterns']:
                if pattern.lower() == user_input:
                    return random.choice(intent['responses']), intent['tag']
        
        # Then check for keyword matches
        for intent in self.data:
            for pattern in intent['patterns']:
                if pattern.lower() in user_input:
                    return random.choice(intent['responses']), intent['tag']
        
        # Check for partial matches with word boundaries
        user_words = user_input.split()
        for intent in self.data:
            for pattern in intent['patterns']:
                pattern_words = pattern.lower().split()
                # Check if any pattern word matches any user word
                if any(p_word in user_words for p_word in pattern_words):
                    return random.choice(intent['responses']), intent['tag']
        
        # Fallback response
        fallback_responses = [i for i in self.data if i['tag'] == 'fallback']
        if fallback_responses:
            return random.choice(fallback_responses[0]['responses']), 'fallback'
        else:
            return "I'm sorry, I don't have the answer to that yet. Please contact the admin office for assistance.", 'fallback'

# Create a singleton instance of the bot
chatbot = NalandaChatbot()