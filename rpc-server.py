import time
import socket
import json
import sys
import nsq


writer = nsq.Writer(['127.0.0.1:4150'])


def get_time(request):
    return {'time': time.time()}


def get_hostname(request):
    return {'hostname': socket.gethostname()}


def get_sum(request):
    return {'sum': (request.get('a') + request.get('b'))}


def do_quit(request):
    sys.exit(0)

handlers = {
    'get_time': get_time,
    'get_hostname': get_hostname,
    'get_sum': get_sum,
    'quit': do_quit
}


def send(dest, data):
    s = json.dumps(data)
    print "RPC --> " + s
    writer.pub(dest, s)


def message_handler(message):
    print "RPC <-- " + message.body
    request = json.loads(message.body)

    call = request.get('call')

    if not call:
        response = {"status": "error", "message": "You need to specify a call"}
    else:
        handler = handlers.get(call)

        if not handler:
            response = {"status": "error", "message": "Unknown RPC call " + call}
        else:
            try:
                response = handler(request)
            except Exception as e:
                response = {"status": "error", "message": "Error executing " + call, "error": str(e)}

    response["src_id"] = message.id

    # We reply to someone if possible
    if request.get('from'):
        send(request['from'], response)
    else:
        print "Message dropped: "+json.dumps(response)
    return True


reader = nsq.Reader(
    topic='rpc', channel='_', message_handler=message_handler,
    lookupd_http_addresses=['http://127.0.0.1:4161'],
    max_in_flight=100
)

print("Ready !")
nsq.run()
