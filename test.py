from tonsdk.contract.wallet import Wallets
from base64 import b64decode
from ton.sync import TonlibClient
from tonsdk.boc import Cell
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


def load_deploy_wallet():
    if 'deploy_wallet' not in os.listdir(f'{os.path.expanduser("~")}/.xton'):
        mnemonic, pk, sk, wallet = Wallets.create('v3r2', 0)
        if '-' in wallet.address.to_string(1, 1, 1) or '_' in wallet.address.to_string(1, 1, 1):
            return load_deploy_wallet()
        store('deploy_wallet', " ".join(mnemonic).encode())
        print(f"Deploy wallet created! | {wallet.address.to_string(1, 1, 1)}")
    else:
        mnemonic = store_value('deploy_wallet').decode().split(' ')
        mnemonic, pk, sk, wallet = Wallets.from_mnemonics(mnemonic)
    return mnemonic, pk, sk, wallet


def main():
    ls_index = store_value('ls_index', b'2').decode()
    store('ls_index', ls_index.encode())
    TonlibClient.enable_unaudited_binaries()
    client = TonlibClient(
        config=store_value('config_url').decode(),
        ls_index=int(ls_index),
    )
    client.init_tonlib()

    mnemonic, pk, sk, wallet = load_deploy_wallet()
    wallet_address = wallet.address.to_string(1, 1, 1)
    wallet_account = client.find_account(wallet_address)

    contract_address = store_value('last_address').decode()
    contract_account = client.find_account(contract_address)

    contract_code = Cell.one_from_boc(b64decode(contract_account.get_state().data))
    contract_data = Cell.one_from_boc(b64decode(contract_account.get_state().data))

    # Write tests

main()

