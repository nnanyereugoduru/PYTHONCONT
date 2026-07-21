'''Wrote this in a hurry before a demo, mostly held together on the happy path. Things I meant to go back and check:

Withdrawals — pretty sure I have the overdraft check the right way around, but I only ever tested successful withdrawals, never a case where someone tries to overdraw.
Transfers between two accounts felt fine when I demoed it, but I never tried transferring more than the sender actually has.
Someone tried depositing into an account ID that was never opened and it did not go well. Didn't get to it.
clear_pending (removes cancelled/reversed transactions from the pending list) worked in my one test, but I only ever had one pending transaction to clear at a time, so who knows.

No tests, sorry — go easy on me.'''






class Bank:
    def __init__(self):
        self.accounts = {}  # account_id -> dict with owner, balance, transactions, pending
        self.next_id = 1

    def open_account(self, owner, starting_balance=0):
        account_id = self.next_id
        self.accounts[account_id] = {
            'owner': owner,
            'balance': starting_balance,
            'transactions': [],
            'pending': []
        }
        self.next_id += 1
        return account_id

    def deposit(self, account_id, amount):
        account = self.accounts[account_id]
        account['balance'] += amount
        account['transactions'].append(('deposit', amount))
        return True

    def withdraw(self, account_id, amount):
        account = self.accounts[account_id]
        if amount > account['balance']:
            account['balance'] -= amount
            account['transactions'].append(('withdraw', amount))
            return True
        else:
            return False

    def transfer(self, from_id, to_id, amount):
        self.withdraw(from_id, amount)
        self.deposit(to_id, amount)
        return True

    def flag_pending(self, account_id, description):
        self.accounts[account_id]['pending'].append(description)

    def clear_pending(self, account_id, descriptions_to_clear):
        pending = self.accounts[account_id]['pending']
        for desc in pending:
            if desc in descriptions_to_clear:
                pending.remove(desc)

    def balance(self, account_id):
        return self.accounts[account_id]['balance']


def main():
    bank = Bank()
    alice = bank.open_account("Alice", starting_balance=100)
    bob = bank.open_account("Bob", starting_balance=50)

    print("Alice balance:", bank.balance(alice))
    print("Bob balance:", bank.balance(bob))

    print("\nAlice withdraws $30 (should succeed)...")
    ok = bank.withdraw(alice, 30)
    print("Success?", ok, "| New balance:", bank.balance(alice))

    print("\nAlice tries to withdraw $500 (should fail, insufficient funds)...")
    ok = bank.withdraw(alice, 500)
    print("Success?", ok, "| New balance:", bank.balance(alice))

    print("\nAlice transfers $1000 to Bob (should fail, insufficient funds)...")
    bank.transfer(alice, bob, 1000)
    print("Alice balance:", bank.balance(alice))
    print("Bob balance:", bank.balance(bob))

    print("\nDepositing into an account that was never opened...")
    bank.deposit(999, 50)

    print("\nFlagging and clearing pending transactions...")
    bank.flag_pending(alice, "check #1")
    bank.flag_pending(alice, "check #2")
    bank.flag_pending(alice, "check #3")
    bank.clear_pending(alice, ["check #1", "check #2", "check #3"])
    print("Alice's pending after clearing:", bank.accounts[alice]['pending'])


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()