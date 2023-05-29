# import bare necessities
import concurrent.futures
import multiprocessing
import os
import subprocess as sp

n = 12                    # number of vertices
total_parts = 5000        # total number of parts (at least 200 for serious business :)

def run_be(part):
    print(f'Processing part {part}...')

    # has this part been already processed - maybe computer crashed in the meantime?
    cwd = os.getcwd()
    graphs_file = os.path.join(cwd, f'be-part-{part}')
    results_file = os.path.join(cwd, f'be-part-{part}-results.csv')
    if os.path.isfile(results_file) and not os.path.isfile(graphs_file):
        print(f'Part {part} already processed - skipping it for now...')
        return results_file

    # put geng in the current directory and
    # then call it to generate graphs in this part
    cmd = f'./geng {n} {part}/{total_parts} > {graphs_file}'
    try:
        sp.check_call(cmd, shell=True)
    except sp.CalledProcessError:
        print(f'geng je nesto zafrknuo stvari s delom {part}...')

    # be-selector.jar should also be in the current directory, so
    # call it to select border-energetic graphs from this part
    cmd = f'java -jar be-selector.jar be-part-{part} 0'
    try:
        sp.check_call(cmd, shell=True)
    except sp.CalledProcessError:
        print(f'be-selector je nesto zafrknuo stvari s delom {part}...')

    # we no longer need graphs from this part
    os.remove(f'be-part-{part}')


if __name__ == '__main__':
    # this would have been the old way
    # params = range(total_parts)
    # with mp.pool(max(mp.cpu_count(), 1)) as pool:
    #     pool.map(run_be, params)

    # the new way using "spawned" subprocesses
    params = range(total_parts)
    ctx = multiprocessing.get_context('spawn')
    with concurrent.futures.ProcessPoolExecutor(mp_context=ctx) as pool:
       pool.map(run_be, params)

    # now put all the separate csv files into a single csv file
    combined_data = []
    missing_parts = []
    for part in params:
        file_name = f'be-part-{part}-results.csv'
        try:
            fin = open(file_name, 'r')
            data = fin.read()
            fin.close()
            combined_data.append(data)
            os.remove(file_name)
        except OSError:
            missing_parts.append(part)

    # write everything together
    fout = open(f'be-total-{n}-results.csv', 'w')
    for item in combined_data:
        fout.write(item)
    fout.close()

    # write the missing parts as well
    fout = open(f'be-missing-parts-{n}.csv', 'w')
    for item in missing_parts:
        fout.write(str(item) + '\n')
    fout.close()
