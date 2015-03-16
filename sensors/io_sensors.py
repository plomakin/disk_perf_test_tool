from discover import provides
from utils import SensorInfo, is_dev_accepted

#  1 - major number
#  2 - minor mumber
#  3 - device name
#  4 - reads completed successfully
#  5 - reads merged
#  6 - sectors read
#  7 - time spent reading (ms)
#  8 - writes completed
#  9 - writes merged
# 10 - sectors written
# 11 - time spent writing (ms)
# 12 - I/Os currently in progress
# 13 - time spent doing I/Os (ms)
# 14 - weighted time spent doing I/Os (ms)

io_values_pos = [
    (3, 'reads_completed', True),
    (5, 'sectors_read', True),
    (6, 'rtime', True),
    (7, 'writes_completed', True),
    (9, 'sectors_written', True),
    (10, 'wtime', True),
    (11, 'io_queue', False),
    (13, 'io_time', True)
]


@provides("block-io")
def io_stat(disallowed_prefixes=('ram', 'loop'), allowed_prefixes=None):
    results = {}
    for line in open('/proc/diskstats'):
        vals = line.split()
        dev_name = vals[2]

        dev_ok = is_dev_accepted(dev_name,
                                 disallowed_prefixes,
                                 allowed_prefixes)

        if dev_ok:
            for pos, name, accum_val in io_values_pos:
                sensor_name = "{0}.{1}".format(dev_name, name)
                results[sensor_name] = SensorInfo(int(vals[pos]), accum_val)
    return results
