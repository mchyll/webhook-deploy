import hmac
import time
import multiprocessing as mp


def deploy(secret, payload):
    pass


def verify_signature(payload: str, signature: str) -> bool:
    payload_bytes = payload.encode('utf-8')
    key_bytes = 'KEY'.encode('utf-8')  # TODO get key from somewhere safe
    digest = hmac.new(key_bytes, payload_bytes, 'sha1')
    expected_signature = 'sha1=' + digest.hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def test():
    with open('secret.txt', 'a+') as f:
        f.seek(0)
        print(f.readline())
        time.sleep(10)


if __name__ == '__main__':
    print(verify_signature('testæøå', 'lol'))
    print(f'hehe :P {time.time()}')

    mp.set_start_method('spawn')
    p1 = mp.Process(target=test)
    p2 = mp.Process(target=test)
    p1.start()
    p2.start()
