from aiohttp import web
import json
from main import verify_signature, load_config, load_secret
import logging
import sys
import threading
import queue
import time
import uuid


__config = load_config()
__secret = load_secret()

__stdout_hander = logging.StreamHandler(sys.stdout)
__formatter = logging.Formatter(
    '%(asctime)s %(name)s: [%(levelname)s] %(message)s')
__stdout_hander.setFormatter(__formatter)
logging.getLogger().addHandler(__stdout_hander)
logging.getLogger('webhook-deploy').setLevel(logging.INFO)


async def github_webhook_handle(req: web.Request):
    log = logging.getLogger('webhook-deploy')

    try:
        payload = await req.text()
        signature = req.headers['X-Hub-Signature']
        delivery_id = req.headers['X-GitHub-Delivery']
        event_type = req.headers['X-GitHub-Event']

        if verify_signature(payload, signature, __secret):
            if event_type == 'ping':
                # TODO: Check against config, log?
                log.info('Got ping event')
                pass
            elif event_type == 'push':
                log.info(
                    f'Yee. Signature: {signature}, delivery id: {delivery_id}, payload: {payload}')
                return web.Response(status=200, text=f'Yee. Signature: {signature}, delivery id: {delivery_id}, payload: {payload}')
        else:
            log.warning(f'Invalid signature from {req.remote}')

    except json.decoder.JSONDecodeError as ex:
        log.error(f'JSON decode error: {ex.msg} from {req.remote}')
        return web.Response(status=400)

    except KeyError as ex:
        log.error(f'Key error: {ex} from {req.remote}')
        return web.Response(status=400)


task_queue = queue.Queue()


async def task_handle(req: web.Request):
    id = uuid.uuid4()
    print(f'web: starting task id {id}')

    task_queue.put(f'task_{id}')

    # x = 0
    # for i in range(50000000):
    #     x += (i % 5751) % 37957

    print(f'web: done with task id {id}')
    return web.Response(body=f'task id {id} done')


def worker():

    print('worker started')
    while True:
        print('waiting for tasks')
        task = task_queue.get()
        print(f'got task {task}')
        x = 0
        for i in range(50000000):
            x += (i % 5751) % 37957
        print('task done')


worker_thread = threading.Thread(target=worker)
worker_thread.start()

app = web.Application()
app.add_routes([web.post('/github-webhook', github_webhook_handle)])
app.add_routes([web.post('/task', task_handle)])

web.run_app(app)
