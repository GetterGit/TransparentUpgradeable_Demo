from brownie import Contract, Box, ProxyAdmin, TransparentUpgradeableProxy
from scripts.helpful_scripts import encode_function_data, get_account

# test delegating calls from proxy to implementation
def test_proxy_delegetes_calls():
    # Arrange
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    # providing no initializer to the encoding function below
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    # Act / Assert
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    assert proxy_box.retrieve() == 0
    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1
