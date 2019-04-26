import json

from indy import did
from indy.payment import create_payment_address
from plenum.client.wallet import Wallet
from plenum.common.util import randomString
from sovtoken.test.wallet import Address


class HelperWallet():
    """
    Helper for dealing with the wallet and addresses.

    # Methods
    - add_new_addresses
    - create_address
    - create_client_wallet
    - create_new_addresses
    - sign_request
    - sign_request_trustees
    - sign_request_stewards
    """

    def __init__(self, looper, client_wallet, trustee_wallets, steward_wallets):
        self._looper = looper
        self._client_wallet = client_wallet
        self._trustee_wallets = trustee_wallets
        self._steward_wallets = steward_wallets
        self.address_map = {}

    def create_address(self):
        """ Create a new address and add it to the address_map """
        address = create_payment_address(self._client_wallet[0], "sov", "{}")
        address = self._looper.loop.run_until_complete(address)
        return address

    def create_new_addresses(self, n):
        """ Create n new addresses """
        return [self.create_address() for _ in range(n)]

    def create_did(self, seed=None, sdk_wallet=None):
        """ Create and store a did in a sdk_wallet. """
        if not seed:
            seed = randomString(32)

        sdk_wallet = sdk_wallet or self._client_wallet

        wallet_handle, _ = sdk_wallet
        config = json.dumps({seed: seed})
        future = did.create_and_store_my_did(wallet_handle, config)

        return self._looper.loop.run_until_complete(future)

    def sign_request_trustees(self, request, number_signers=4):
        """ Sign a request with trustees. """
        assert number_signers <= len(self._trustee_wallets)
        return self.sign_request(request, self._trustee_wallets[:number_signers])

    def sign_request_stewards(self, request, number_signers=4):
        """ Sign a request with stewards. """
        assert number_signers <= len(self._steward_wallets)
        return self.sign_request(request, self._steward_wallets[:number_signers])

    def sign_request(self, request, wallets):
        """ Sign a request with wallets from plenum/client/wallet """
        for wallet in wallets:
            wallet.do_multi_sig_on_req(request, identifier=wallet.defaultId)
        return request
