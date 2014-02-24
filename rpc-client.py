import tornado.ioloop
import json
import socket

import nsq


ephemeral = True

me = "client-" + socket.gethostname()


def message_handler(message):
    print "RPC <-- " + message.body
    return True


reader = nsq.Reader(
    topic=me, channel='_#ephemeral', message_handler=message_handler,
    lookupd_http_addresses=['http://127.0.0.1:4161'],
    max_in_flight=100
)
writer = nsq.Writer(['127.0.0.1:4150'])


def send(msg):
    if not msg.get('from'):
        msg['from'] = me

    data = json.dumps(msg)
    print "RPC --> " + data
    writer.pub('rpc', data)


def request_time():
    send({"call": "get_time"})


def request_hostname():
    send({"call": "get_hostname"})


def request_sum():
    send({"call": "get_sum", "a": 40, "b": 2})


def request_stuff():
    send({"call": "stuff", "hint": "It won't work"})


def request_with_wrong_from():
    send({"call": "stuff", "from": "rpc"})


def request_quit():
    send({"call": "quit"})


tornado.ioloop.PeriodicCallback(request_time, 1000).start()
tornado.ioloop.PeriodicCallback(request_hostname, 1000).start()
tornado.ioloop.PeriodicCallback(request_sum, 1000).start()
tornado.ioloop.PeriodicCallback(request_stuff, 1000).start()
tornado.ioloop.PeriodicCallback(request_with_wrong_from, 1000).start()
# tornado.ioloop.PeriodicCallback(request_quit, 3000).start()
nsq.run()
