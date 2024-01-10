#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

'''An Intercom wrapper employing different implementations of bit-rate control 
and computing the RMSE over the sent and received chunks (if sent and received 
in a single InterCom instance).'''

import minimal
import buffer
import logging
import numpy as np
import matplotlib.pyplot as plt
import os
import signal
import BR_control_no
import BR_control_add_lost
import BR_control_lost
import BR_control_conservative

minimal.parser.add_argument("-z", "--bitrate_imp", type=int, default=0, help="Select bitrate control implementation")

class RMSEChunks_no(BR_control_no.BR_Control_No):
    def __init__(self):
        logging.disable(logging.CRITICAL)
        super().__init__()
        #logging.info(__doc__)

        self.sent_chunks = np.empty((1024, 2))
        self.recd_chunks = np.empty((1024, 2))
    
    def _read_io_and_play(self, outdata, frames, time, status):
        read_chunk = super()._read_io_and_play(outdata, frames, time, status)
        self.sent_chunks = np.append(self.sent_chunks, read_chunk)
        return read_chunk
    
    def receive_and_buffer(self):
        chunk_number = super().receive_and_buffer()
        self.recd_chunks = np.append(self.recd_chunks, self._buffer[chunk_number % self.cells_in_buffer])
        return chunk_number
    
    def read_chunk_from_file(self):
        chunk = self.wavfile.buffer_read(minimal.args.frames_per_chunk, dtype='int16')
        #print(len(chunk), args.frames_per_chunk)
        if len(chunk) < minimal.args.frames_per_chunk*4:
            logging.warning("Input exhausted! :-/")
            #print(self.recd_chunks.dtype)
            #print(self.sent_chunks.dtype)
            #print(self.recd_chunks)

            rmse = np.sqrt(np.mean(np.square(np.array(self.recd_chunks, dtype='int16') - np.array(self.sent_chunks, dtype='int16'))))
            print(rmse)
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            return self.zero_chunk
        chunk = np.frombuffer(chunk, dtype=np.int16)
        #try:
        chunk = np.reshape(chunk, (minimal.args.frames_per_chunk, self.NUMBER_OF_CHANNELS))
        #except ValueError:
            #logging.warning("Input exhausted! :-/")
            #pid = os.getpid()
            #os.kill(pid, signal.SIGINT)
            #self.input_exhausted = True
        return chunk

    #def run(self):
    #    super().run()
        
    #    rmse = np.sqrt(np.mean((self.recd_chunks - self.sent_chunks)**2))

    #    print(rmse)
        
        #rmse_chunks_ch1 = rmse_chunks[:, 0]
        #rmse_chunks_ch2 = rmse_chunks[:, 1]

        #plt.plot(rmse_chunks_ch1)

class RMSEChunks_add_lost(RMSEChunks_no, BR_control_add_lost.BR_Control_Add_Lost):
    pass

class RMSEChunks_lost(RMSEChunks_no, BR_control_lost.BR_Control_Lost):
    pass

class RMSEChunks_conservative(RMSEChunks_no, BR_control_conservative.BR_Control_Conservative):
    pass

np.seterr(divide='ignore', invalid='ignore')

try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    logging.warning("Unable to import argcomplete (optional)")

if __name__ == "__main__":
    minimal.parser.description = __doc__

    try:
        argcomplete.autocomplete(minimal.parser)
    except Exception:
        logging.warning("argcomplete not working :-/")

    minimal.args = minimal.parser.parse_known_args()[0]

    if minimal.args.list_devices:
        print("Available devices:")
        print(sd.query_devices())
        quit()

    intercom = RMSEChunks_no()
    
    match minimal.args.bitrate_imp:
        case 0:
            pass
        case 1:
            intercom = RMSEChunks_add_lost()
        case 2:
            intercom = RMSEChunks_lost()
        case 3:
            intercom = RMSEChunks_conservative()
    
    try:
        intercom.run()
    except KeyboardInterrupt:
        #minimal.parser.exit("\nSIGINT received")
        minimal.parser.exit()
    finally:
        intercom.print_final_averages()