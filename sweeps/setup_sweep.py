import os, os.path as path, shutil
import hashlib, json
import numpy
import itertools

from .sweep_utils import get_timestamp

def create_rfs(sim, sweep):
    sweep_file = path.join(sim,sweep)
    for rf, params in read_sweep(sweep_file):
        rf_path = path.join(sim,'rfs',rf)
        if not path.exists(rf_path):
            os.mkdir(rf_path)
            with open(path.join(rf_path,'params.json'), 'w+') as file:
                file.write(params)
            open(path.join(rf_path,'status.txt'),'w+').close()
            open(path.join(rf_path,'log.txt'),'w+').close()
    sweep = get_timestamp() + '.create.json'
    history_path = path.join(sim,'history')
    if not path.exists(history_path):
        os.mkdir(history_path)
    shutil.copyfile(sweep_file, path.join(history_path,sweep))

def delete_rfs(sim, sweep):
    sweep_file = path.join(sim,sweep)
    for rf,_ in read_sweep(sweep_file): #TODO: Check equality of params.json?
        rf_path = path.join(sim,'rfs',rf)
        if path.exists(rf_path):
            shutil.rmtree(rf_path)
    sweep = get_timestamp() + '.delete.json'
    history_path = path.join(sim,'history')
    if not path.exists(history_path):
        os.mkdir(history_path)
    shutil.copyfile(sweep_file, path.join(history_path,sweep))

def read_sweep(sweep_file):
    with open(sweep_file) as file:
        sweep = json.load(file)

    iterable_value = dict()
    iterable_value['constant'] = lambda value : [value]
    iterable_value['manual'] = lambda value : numpy.array(value)
    iterable_value['linspace'] = lambda value : numpy.linspace(*value)

    parameter_keys = list(sweep.keys())
    parameter_values = [iterable_value[item['sweep_type']](item['value'])  \
                                for item in sweep.values()]

    for values in itertools.product(*parameter_values):
        params = dict(zip(parameter_keys,values))
        params = json.dumps(params,indent=4,sort_keys=True)
        rf = hashlib.md5(params.encode('utf-8')).hexdigest()[:16]
        yield (rf, params)
