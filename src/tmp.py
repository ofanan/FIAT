import numpy as np
import hashlib
import mmh3
import datetime
import scipy.stats as st
from printf import printf


class SketchStatistics:
    def __init__(self, width, depth):
        self.width, self.depth = width, depth
        self.counters = np.zeros([depth, width], dtype=np.int32)
        self.hash_functions = [lambda flow: mmh3.hash(str(flow)),
                               lambda flow: int(hashlib.sha256(str(flow).encode()).hexdigest()[:8], 16),
                               lambda flow: int(hashlib.sha1(str(flow).encode()).hexdigest()[:8], 16),
                               lambda flow: int(hashlib.blake2s(str(flow).encode()).hexdigest()[:8], 16)]
        self.conf_interval = lambda relative_errors, avg_error, conf_lvl=0.99: st.t.interval(conf_lvl, len(relative_errors) - 1, loc=avg_error, scale=st.sem(relative_errors)) if np.std(
                            relative_errors) > 0 else [avg_error, avg_error]

    def increment(self, flow, count=1):
        for i in range(self.depth):
            self.counters[i][self.hash_functions[i](flow) % self.width] += count

    def query(self, flow):
        return min(self.counters[i][self.hash_functions[i](flow) % self.width] for i in range(self.depth))

    def printToFile(self):
        start_time = datetime.datetime.now()
        num_flows = 100  # default value
        overall_num_of_increments = 1000  # default value
        per_flow_counters = {}
        relative_errors = np.zeros(overall_num_of_increments, dtype=np.float32)
        for i in range(overall_num_of_increments):
            flow = np.random.randint(num_flows)
            self.increment(flow=flow)
            per_flow_counters[flow] = per_flow_counters.get(flow, 0) + 1
            relative_errors[i] = abs(self.query(flow) - per_flow_counters[flow]) / per_flow_counters[flow]

        avg_error = np.mean(relative_errors)
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        elapsed_seconds = elapsed_time.total_seconds()
        with open("results.txt", "a+") as results_file:
            printf(results_file, '\nResult of width={}, depth={}\n'.format(self.width, self.depth))
            printf(results_file, 'Average relative error:{}\n'.format(avg_error))
            # print(f"99% confidence interval: {self.conf_interval(relative_errors, avg_error)}", file=results_file)
            printf(results_file, f"99 percent confidence interval: {self.conf_interval(relative_errors, avg_error)}\n")
            printf(results_file, 'Elapsed time:{:.2f} seconds\n\n'.format(elapsed_seconds))


def main():
    sketch1 = SketchStatistics(width=3, depth=2)
    sketch1.printToFile()
    # sketch2 = SketchStatistics(width=7, depth=3)
    # sketch2.printToFile()
    # sketch3 = SketchStatistics(width=9, depth=3)
    # sketch3.printToFile()
    # sketch4 = SketchStatistics(width=12, depth=4)
    # sketch4.printToFile()
    # sketch5 = SketchStatistics(width=15, depth=4)
    # sketch5.printToFile()


if __name__ == '__main__':
    main()