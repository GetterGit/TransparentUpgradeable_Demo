from brownie import accounts, network, config
import eth_utils

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


# *args meaning it can take any number of arguments and store them as a list. E.g. initializer=box.store, 1, 2, 3, 4
def encode_function_data(initializer=None, *args):
    # first, working around the case when we don't have any args or initializer at all
    if len(args) == 0 or not initializer:
        # returning an empy hexstring
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    upgrade_tx = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            # .upgradeAndCall() is used because we also have an initializer to call
            upgrade_tx = proxy_admin_contract.upgradeAndCall(
                proxy,
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            # if no initializer, then using just upgrade()
            upgrade_tx = proxy_admin_contract.upgrade(
                proxy, new_implementation_address, {"from": account}
            )
    else:
        # if no proxy_admin_contract, then the account is the admin
        # first, check if there is an initializer still
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            upgrade_tx = proxy.upgradeToAndCall(
                new_implementation_address, encoded_function_call, {"from": account}
            )
        else:
            upgrade_tx = proxy.upgradeTo(new_implementation_address, {"from": account})
    return upgrade_tx
