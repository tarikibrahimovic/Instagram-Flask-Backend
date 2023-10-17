# from flask import current_app
#
user_sockets = []
#
#
# def get_sock():
#     return current_app.extensions['sock']
#
#
# def register_socket_routes(sock):
#     @sock.route('/echo/<int:user_id>')
#     def echo(sock, user_id):
#         while True:
#             user_sockets.append({"user_id": user_id, "socket": sock})
#             print(user_id)
#             data = sock.receive()
#             # send this to only one client
#             sock.send(user_sockets)
#
#
# def setup():
#     register_socket_routes(get_sock())
