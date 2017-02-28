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
        process = partial(process_read, model, section='template')

        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(None, process, filename)
        result = yield from task

        if result is not None:
            [(fname, (seq, qual), score, len_features),
             (network_time, decode_time)] = result
            result = "@{}\n{}\n+\n{}\n".format(fname, seq, qual)
        return result


@asyncio.coroutine
def go():
    server =  yield from rpc.serve_rpc(ReadHandler(),
                                       bind='tcp://127.0.0.1:5555')
    
    client = yield from rpc.connect_rpc(connect='tcp://127.0.0.1:5555')
    
    ret = yield from client.call.basecall('/Users/cwright/git/nanonet3_fresh/nanonet/sample_data/904896_ch170_read104_strand.fast5')
    print(ret)


def main():
    event_loop = asyncio.get_event_loop()
    executor = PoolExecutor(max_workers=4)
    event_loop.set_default_executor(executor)
    try:
        event_loop.run_until_complete(go())
    finally:
        event_loop.close()


if __name__ == '__main__':
    main()
