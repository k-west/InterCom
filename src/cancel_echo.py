#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import minimal
import buffer
import logging
import sounddevice as sd

minimal.parser.add_argument("-x", "--alpha", type=int, default=3, help="Alpha parameter for echo cancellation")
minimal.parser.add_argument("-y", "--delay", type=float, default=0.0165, help="Delay between speaker and microphone")

class EchoCancelling(buffer.Buffering):
    def __init__(self):
        super().__init__()

    def cancel_out_echo(self, indata):
        chunk_delay = int((minimal.args.frames_per_second * minimal.args.delay) / minimal.args.frames_per_chunk)

        subtr_chunk = self._buffer[(self.played_chunk_number + chunk_delay) % self.cells_in_buffer]
        subtr_chunk = subtr_chunk.reshape(minimal.args.frames_per_chunk, self.NUMBER_OF_CHANNELS) # for some reason the chunk is (2048,) instead of (1024, 2)

        # print(indata)
        # print(subtr_chunk)

        indata -= minimal.args.alpha * subtr_chunk

        return indata

    def _record_io_and_play(self, indata, outdata, frames, time, status):
        self.chunk_number = (self.chunk_number + 1) % self.CHUNK_NUMBERS
        echo_corr_indata = self.cancel_out_echo(indata)
        packed_chunk = self.pack(self.chunk_number, echo_corr_indata)
        self.send(packed_chunk)
        chunk = self.unbuffer_next_chunk()
        self.play_chunk(outdata, chunk)

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

    intercom = EchoCancelling()
    
    try:
        intercom.run()
    except KeyboardInterrupt:
        minimal.parser.exit("\nSIGINT received")
    finally:
        intercom.print_final_averages()
