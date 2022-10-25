
from subprocess import Popen, PIPE
from hashlib import sha256
import sys, os
import setuptools


def build_artifacts(name, imports=None):
    name = sha256(name.encode()).hexdigest()[:10]

    proc = Popen('pip3 show xton', shell=True, stdout=PIPE)
    out, err = proc.communicate()
    xton_path = next(i for i in out.decode().split('\n') if i.split(':')[0] == 'Location').split(': ')[-1]

    imports = imports or []
    if 'stdlib.func' not in imports:
        imports = [xton_path + '/xton/stdlib.func', *imports]

    try:
        os.mkdir('.build')
    except FileExistsError:
        pass

    with open(f".build/{name}.fif", 'wb') as file: file.write(b'')
    with open(f".build/{name}.cell.fif", 'wb') as file: file.write(b'')
    with open(f".build/{name}.cell", 'wb') as file: file.write(b'')

    Popen(f'export FIFTPATH="{xton_path}/xton/fift-libs"', shell=True).wait()
    print(f'export FIFTPATH="{xton_path}/xton/fift-libs"')

    print(f"Building {name}...")
    proc = Popen(f'func -APS -o .build/{name}.fif {" ".join([x for x in imports])}', shell=True)
    proc.wait()
    out, err = proc.communicate()
    if err:
        print(f"Error while building {name}:\n{err.decode()}")
        sys.exit(1)

    fift_source_cell = ''
    with open(f".build/{name}.fif", 'r') as file:
        fift_source_cell += file.read() + '\n'

    fift_source_cell += f'boc>B ".build/{name}.cell" B>file'
    with open(f".build/{name}.cell.fif", 'w') as file:
        file.write(fift_source_cell)

    print(f"Compiling {name}...")
    proc = Popen(f'fift .build/{name}.cell.fif', shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    out, err = proc.communicate()
    if err:
        print(f"Error while compiling {name}:\n{err.decode()}")
        sys.exit(1)

    print(f"Compile output:\n{out.decode()}")

    with open(f".build/{name}.cell", 'rb') as file:
        code_cell = file.read()

    with open(f".build/{name}.hex", 'w') as f:
        f.write(code_cell.hex().upper())

    print(f"Artifact {name} compiled successfully! | {sha256(code_cell).hexdigest()[:10]}")

    return {
        'code': code_cell,
        'hex': code_cell.hex().upper()
    }
