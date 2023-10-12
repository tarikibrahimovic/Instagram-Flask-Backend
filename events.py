from flask import current_app

sock = current_app.extensions['sock']

user_sockets = []

@sock.route('/echo/<int:user_id>')
def echo(sock, user_id):
    while True:
        user_sockets.append({"user_id": user_id, "socket": sock})
        print(user_id)
        data = sock.receive()
        #send this to only one client
        sock.send(user_sockets)
