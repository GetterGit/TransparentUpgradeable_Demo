from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade
import pytest


def test_proxy_upgrades():
    # Arrange
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    # Act / Assert
    # now we should revert when trying to call BoxV2 function on the current proxy which is tied to the Box implementation which doesn't have this function
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})
    # now, we upgrade the proxy to the BoxV2 implementation and calling increment() again
    upgrade(account, proxy, box_v2.address, proxy_admin_contract=proxy_admin)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
