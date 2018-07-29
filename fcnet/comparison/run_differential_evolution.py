import os
import sys
import json
import argparse
import ConfigSpace


sys.path.append("/home/kleinaa/devel/git/nas_benchmark_github/tabular_benchmarks")
from wrn_cifar10_3h import WRNCIFAR103HBenchmark
from fcnet_year_prediction import FCNetYearPredictionBenchmark
from fcnet_benchmark import FCNetBenchmark

from scipy.optimize import differential_evolution


parser = argparse.ArgumentParser()
parser.add_argument('--run_id', default=0, type=int, nargs='?', help='unique number to identify this run')
parser.add_argument('--benchmark', default="wrn_cifar10", type=str, nargs='?', help='specifies the benchmark')
parser.add_argument('--n_iters', default=100, type=int, nargs='?', help='number of iterations for optimization method')
parser.add_argument('--output_path', default="./", type=str, nargs='?',
                    help='specifies the path where the results will be saved')
parser.add_argument('--data_dir', default="./", type=str, nargs='?', help='specifies the path to the tabular data')

args = vars(parser.parse_args())

if args.benchmark == "wrn_cifar10":
    b = WRNCIFAR103HBenchmark(data_dir=args.data_dir)

elif args.benchmark == "fcnet_regression":
    b = FCNetYearPredictionBenchmark(data_dir=args.data_dir)

elif args.benchmark == "protein_structure":
    b = FCNetBenchmark(dataset=args.data_dir)

output_path = args.output_path
os.makedirs(os.path.join(output_path), exist_ok=True)

cs = b.get_configuration_space()


def obj_wrapper(x):
    config = dict()

    for i, h in enumerate(cs.get_hyperparameters()):

        if type(h) == ConfigSpace.hyperparameters.OrdinalHyperparameter:
            config[h.name] = h.sequence[int(round(x[i]))]
        else:
            config[h.name] = h.choices[int(round(x[i]))]

    y, c = b.objective_function(config)

    return y


lower = []
upper = []

for h in cs.get_hyperparameters():
    lower.append(0)
    if type(h) == ConfigSpace.hyperparameters.OrdinalHyperparameter:
        upper.append(len(h.sequence) - 1)
    else:
        upper.append(len(h.choices) - 1)

bounds = list(zip(lower, upper))

differential_evolution(obj_wrapper, bounds)

res = b.get_results()

fh = open(os.path.join(output_path, 'run_%d.json' % args.run_id), 'w')
json.dump(res, fh)
fh.close()
