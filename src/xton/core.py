
from subprocess import Popen, PIPE
from hashlib import sha256
import sys, os


def store(key, value: bytes):
    if not os.path.isdir(f'{os.path.expanduser("~")}/.xton'):
        os.mkdir(f'{os.path.expanduser("~")}/.xton')

    with open(f'{os.path.expanduser("~")}/.xton/{key}', 'wb') as file:
        file.write(value)


def store_value(key, base=None):
    if not os.path.isdir(f'{os.path.expanduser("~")}/.xton'):
        return base

    if key not in os.listdir(f'{os.path.expanduser("~")}/.xton'):
        return base

    with open(f'{os.path.expanduser("~")}/.xton/{key}', 'rb') as file:
        return file.read()


def custom_executables():
    return {
        line.split('=')[0]: line.split('=')[1] for line in store_value('executables', b'').decode().split('\n') if '=' in line
    }


def build_artifacts(name, imports=None):
    executables = custom_executables()
    name = sha256(name.encode()).hexdigest()[:10]

    proc = Popen('pip3 show xton', shell=True, stdout=PIPE, executable='/bin/bash')
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

    Popen(f'export FIFTPATH="{xton_path}/xton/fift-libs"', shell=True, executable='/bin/bash').wait()

    print(f"Building {name}...")
    proc = Popen(f'{executables.get("func", "func")} -APS -o .build/{name}.fif {" ".join([x for x in imports])}', shell=True, executable='/bin/bash')
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
    fift_env = os.environ.copy()
    fift_env['FIFTPATH'] = f"{xton_path}/xton/fift-libs"
    proc = Popen(f'{executables.get("fift", "fift")} .build/{name}.cell.fif', shell=True, stdout=PIPE, stderr=PIPE, env=fift_env, executable='/bin/bash')
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
