import argparse
import sys
import os
import glob
import platform
from multiprocessing import freeze_support
from timeit  import default_timer as now
import asyncio
from aiozmq import rpc
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from functools import partial
import pkg_resources

from nanonet.nanonetcall import process_read
default_model = pkg_resources.resource_filename('nanonet', 'data/r9_template.npy')

class ReadHandler(rpc.AttrHandler):

    @rpc.method
    @asyncio.coroutine
    def basecall(self, filename, model=default_model):
        process = partial(process_read, model, section='template',
            write_events=False, max_len=40000
        )

        loop = asyncio.get_event_loop()
        print("Scheduling {}.".format(filename))
        task = loop.run_in_executor(None, process, filename)
        result = yield from task
        print("Finished {}.".format(filename))

        if result is not None:
            [(fname, (seq, qual), score, len_features),
             (network_time, decode_time)] = result
            result = "@{}\n{}\n+\n{}\n".format(fname, seq, qual)
        return result


@asyncio.coroutine
def server(port):
    server =  yield from rpc.serve_rpc(
        ReadHandler(), bind='tcp://127.0.0.1:{}'.format(port)
    )


@asyncio.coroutine
def client(port, files):
    client = yield from rpc.connect_rpc(
        connect='tcp://127.0.0.1:{}'.format(port)
    )
    loop = asyncio.get_event_loop()
    files = glob.glob(os.path.join(files, '*.fast5'))

    def print_result(f):
        print(f.result())

    t0 = now()
    futures = [client.call.basecall(x) for x in files]
    for future in futures:
        future.add_done_callback(print_result)
    yield from asyncio.gather(*futures)
    t1 = now()
    print("Processed {} reads in {}s.".format(len(files), t1 - t0))


@asyncio.coroutine
def wakeup():
    while True:
        yield from asyncio.sleep(1)


def main(prog, port, files):
    print("Starting {} on port {}".format(prog, port))
    event_loop = asyncio.get_event_loop()
    executor = PoolExecutor(max_workers=4)
    event_loop.set_default_executor(executor)
    if platform.system() == 'Windows':
        #SO/27480967
        asyncio.async(wakeup())
    try:
        if prog == 'server':
            event_loop.create_task(server(port))
            event_loop.run_forever()
        else:
            event_loop.run_until_complete(client(port, files))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    freeze_support()
    parser = argparse.ArgumentParser('Simple zmq server and client demo.')
    parser.add_argument('program', choices=['server', 'client'], help='Choice of process.')
    parser.add_argument('--port', type=int, default=5555, help='Communication port.')
    parser.add_argument('--input', default=[], help='Files to baecall.')
    args = parser.parse_args()
    main(args.program, args.port, args.input)
