
from .core import build_artifacts, store, store_value
from .common import NETWORK_CONFIGS
from base64 import b64decode
from tonsdk.contract.wallet import Wallets
from tonsdk.contract import Contract
from tonsdk.boc import Cell
from ton.sync import TonlibClient
from ton.tl.types import Tvm_StackEntryNumber, Tvm_NumberDecimal
import sys, os
import time


def invalid_usage():
    print("""Commands:
build <path> - compile func, create artifacts
deploy <path> - upload smartcontract to network
config <url> - set config url (or testnet, mainnet)
wallet - show deploy-wallet and balance""")
    sys.exit(1)


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


def build_contract(code, data):
    class AbstractContract(Contract):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def create_data_cell(self):
            return Cell.one_from_boc(self.options['data'])

    return AbstractContract(code=Cell.one_from_boc(code), data=data)


def main():
    args = sys.argv[1:]
    if not args:
        invalid_usage()

    mnemonic, pk, sk, wallet = load_deploy_wallet()
    wallet_address = wallet.address.to_string(1, 1, 1)

    command = args[0]
    args = args[1:]
    if command == 'set':
        store(args[0], args[1].encode())
        print(f"Value {args[0]} set to {args[1]}")
        return
    if command == 'get':
        print('Value:', store_value(args[0]).decode())
        return
    elif command == 'config':
        if not args:
            invalid_usage()

        new_url = NETWORK_CONFIGS.get(args[0]) or args[0]
        store('config_url', new_url.encode())
        print(f"Config url set to {new_url}")
        return
    elif command == 'build':
        if not args:
            invalid_usage()

        result = build_artifacts(args[-1], args)
        print('Code Cell: ' + result['hex'])
        return

    ls_index = store_value('ls_index', b'2').decode()
    store('ls_index', ls_index.encode())
    TonlibClient.enable_unaudited_binaries()
    client = TonlibClient(
        config=store_value('config_url').decode() or NETWORK_CONFIGS['testnet'],
        ls_index=int(ls_index),
    )
    client.init_tonlib()

    wallet_account = client.find_account(wallet_address)
    if wallet_account.get_balance() <= 0:
        print(f"Deploy wallet is empty! | {wallet_address}")
        return

    if not wallet_account.get_state().code:
        query = wallet.create_init_external_message()
        client.send_boc(query['message'].to_boc(False))
        print(f"Deploy wallet initialized! | {wallet_address}")
        time.sleep(5)
        return main()

    elif command == 'deploy':
        if len(args) < 2:
            invalid_usage()

        result = build_artifacts(args[-1], args[1:])

        store('last_code', result['hex'].encode())
        store('last_data', args[0].encode())
        contract = build_contract(result['code'], data=args[0])
        contract_address = contract.address.to_string(1, 1, 1)
        store('last_address', contract_address.encode())
        print(f"Contract address: {contract_address}")
        contract_account = client.find_account(contract_address)
        contract_state = contract_account.get_state()
        if bool(contract_state.code) is True:
            print(f"Contract already deployed! | {contract_address}")
            return

        while bool(contract_state.code) is False:
            query = wallet.create_transfer_message(
                contract_address, client.to_nano(0.05), wallet_account.seqno(),
                state_init=contract.create_state_init()['state_init']
            )
            client.send_boc(query['message'].to_boc(False, False))
            print(f"Sent deploy message! | {contract_address}")
            contract_state = contract_account.get_state(force=True)
            time.sleep(5)

        print(f"Contract deployed! | {contract_address}")
        return
    elif command == 'state':
        contract = build_contract(store_value('last_code').decode(), data=store_value('last_data').decode())
        contract_address = contract.address.to_string(1, 1, 1)
        print(f"Contract address: {contract_address}")
        contract_account = client.find_account(contract_address)
        contract_state = contract_account.get_state()
        if bool(contract_state.code):
            print(f"""Contract is deployed
            
Code: {b64decode(contract_state.code).hex()}
Data: {b64decode(contract_state.data).hex()}
Balance: {contract_account.get_balance()}""")
        else:
            print(f"""Contract is not deployed""")
    elif command == 'run_get_method':
        if not args: invalid_usage()
        contract = build_contract(store_value('last_code').decode(), data=store_value('last_data').decode())
        contract_address = contract.address.to_string(1, 1, 1)
        print(f"Contract address: {contract_address}")
        contract_account = client.find_account(contract_address)
        contract_state = contract_account.get_state()
        assert bool(contract_state.code), "Contract is not deployed"

        method = args[0]
        args = args[1:]
        call_args = []
        for e in args:
            if isinstance(e, int):
                call_args.append(Tvm_StackEntryNumber(Tvm_NumberDecimal(e)))

        return contract_account.run_get_method(method, call_args)
    elif command == 'wallet':
        print(f"""Your deploy wallet is {wallet_address}. His balance is {round(client.from_nano(wallet_account.get_balance()), 2)} TON""")





