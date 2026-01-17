"""
Flask web application for chat interactions using LaunchDarkly AI Configs and AWS Bedrock.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chat_interaction import ChatInteraction, AI_CONFIG_KEY, JUDGE_CONFIG_KEY
from ldclient import Context
import ldclient

app = Flask(__name__, static_folder='static')
CORS(app)

# Store chat sessions (in production, use a proper session store)
chat_sessions = {}


def get_or_create_chat_session(session_id: str, user_id: str = None) -> ChatInteraction:
    """Get existing chat session or create a new one."""
    if session_id not in chat_sessions:
        # Create user context
        user_context = Context.builder(user_id or f"user-{session_id}") \
            .set("firstName", "User") \
            .set("lastName", "Demo") \
            .set("email", f"user-{session_id}@example.com") \
            .build()
        
        chat = ChatInteraction(user_context, AI_CONFIG_KEY, JUDGE_CONFIG_KEY)
        if not chat.initialize():
            raise Exception("Failed to initialize chat session")
        
        chat_sessions[session_id] = chat
    
    return chat_sessions[session_id]


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('static', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat message requests."""
    try:
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        user_id = data.get('user_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create chat session
        chat = get_or_create_chat_session(session_id, user_id)
        
        # Check if judge is available first
        judge_available = chat.is_judge_available()
        
        if judge_available:
            # Get AI response with judge evaluation
            result = chat.chat_with_judge(message)
            judge_result = result.get('judge')
        else:
            # Get AI response without judge
            response_text = chat.chat(message)
            result = {'response': response_text}
            judge_result = None
        
        return jsonify({
            'response': result['response'],
            'judge': judge_result,
            'judge_available': judge_available,
            'session_id': session_id,
            'model': chat.get_model_info()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for a session."""
    try:
        session_id = request.args.get('session_id', 'default')
        
        if session_id not in chat_sessions:
            return jsonify({'history': [], 'model': None})
        
        chat = chat_sessions[session_id]
        history = chat.get_conversation_history()
        
        return jsonify({
            'history': history,
            'model': chat.get_model_info()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation history for a session."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in chat_sessions:
            chat_sessions[session_id].reset()
            return jsonify({'message': 'Conversation reset successfully'})
        else:
            return jsonify({'message': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model', methods=['GET'])
def get_model():
    """Get model information for a session."""
    try:
        session_id = request.args.get('session_id', 'default')
        user_id = request.args.get('user_id')
        
        # Get or create chat session (this will initialize it)
        chat = get_or_create_chat_session(session_id, user_id)
        
        return jsonify({
            'model': chat.get_model_info(),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

