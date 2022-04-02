from brownie import (
    network,
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()} ...")
    # setting box as our implementation contract
    box = Box.deploy({"from": account})
    # now, we need to hook up a proxy admin to our implementation contract
    proxy_admin = ProxyAdmin.deploy({"from": account})
    # now, we need to hook up both implementation contract and proxy admin contract to the actual proxy contract
    # proxy contracts don't have a constructor. Instead, they have an initializer function which we can choose from the existing functions.
    # the moment we deploy our proxy, we shall call the initializer function
    # setting up the sotre() function as initializer and initializing it at '1'
    # initializer = box.store, 1
    # now, we need to turn initializer into the bytes form
    box_encoded_initializer_function = (
        encode_function_data()
    )  # in this instance, the initializer is set to nothing
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        # sometimes, proxies have hard times figuring out the gas limit, so worthy to input it manually
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, we can now upgrade to V2.")
    # now, we can start calling Box functions from the proxy contract
    # below, we are assigning the ABI of the Box contract to the proxy address. This is gonna work because Proxy is gonna delegate all its calls to the Box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    store_tx = proxy_box.store(1, {"from": account})
    store_tx.wait(1)
    # in the below print(), we are going to delegate the call to the Box contract
    print(proxy_box.retrieve())
    print("=================================")
    # now, we can point to proxy and it's gonna be delegating to the most recent Box contract version given we set it as the actual implementation
    # for this, we need to upgrade the proxy to delegate to a new implementation
    box_v2 = BoxV2.deploy({"from": account})
    # !!! even though we updated the contract, the storage of the previous contract stayed in proxy - hence the current value would be one if we were to query it with retrieve()
    upgrade_tx = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    increment_tx = proxy_box.increment({"from": account})
    increment_tx.wait(1)
    print(proxy_box.retrieve())
