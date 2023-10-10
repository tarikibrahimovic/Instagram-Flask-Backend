from flask import current_app

socketio = current_app.extensions['socketio']


@socketio.on('connect')
def connect():
    print('Client connected')
