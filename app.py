# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request

clients = []

@socketio.on('connect')
def handle_connect():
    global clients
    if len(clients) >= 2:
        emit('full', {'msg': '房間已滿'})
        return
    sid = request.sid
    clients.append(sid)
    color = 'black' if len(clients) == 1 else 'white'
    emit('assign_color', {'color': color})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gomoku-secret'
socketio = SocketIO(app)

# 儲存遊戲狀態
board = [['' for _ in range(15)] for _ in range(15)]
current_player = 'black'
game_over = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('move')
def handle_move(data):
    global current_player, game_over
    x, y = data['x'], data['y']
    if board[y][x] or game_over:
        return

    board[y][x] = current_player
    emit('move_made', {'x': x, 'y': y, 'player': current_player}, broadcast=True)

    if check_winner(x, y):
        emit('game_over', {'winner': current_player}, broadcast=True)
        game_over = True
        return

    current_player = 'white' if current_player == 'black' else 'black'

def check_winner(x, y):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        for d in [1, -1]:
            nx, ny = x, y
            while True:
                nx += dx * d
                ny += dy * d
                if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == current_player:
                    count += 1
                else:
                    break
        if count >= 5:
            return True
    return False

@socketio.on('reset')
def handle_reset():
    global board, current_player, game_over
    board = [['' for _ in range(15)] for _ in range(15)]
    current_player = 'black'
    game_over = False
    emit('reset_board', broadcast=True)

if __name__ == '__main__':
    import eventlet
    socketio.run(app, host='0.0.0.0', port=10000)
