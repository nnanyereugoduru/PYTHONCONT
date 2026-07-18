'''Dev note:

Left this half-finished before I switched teams — sorry to dump it on you. From memory, here's what was nagging me:

Checking out a book that's already checked out should obviously fail, but I'm not 100% sure it actually does — never stress-tested it.
The overdue calculation gave me a weird number once and I never figured out if it was a fluke or my math being wrong.
Returning a book nobody checked out should probably not work either, but I never tested what actually happens if you try.
member_history looked right in my one test member, but something about how I'm building it up across multiple calls bugs me in hindsight — I have a feeling it's not clean between different members.

No unit tests, apologies. Have fun.'''
from datetime import date

class Library:
    def __init__(self):
        self.books = {}  # title -> dict with 'checked_out_by', 'due_date'
        self.history = {}  # member -> list of titles (shared default gotcha risk elsewhere too, keep an eye out)

    def add_book(self, title):
        self.books[title] = {'checked_out_by': None, 'due_date': None}

    def checkout(self, title, member, due_date):
        book = self.books[title]
        book['checked_out_by'] = member
        book['due_date'] = due_date

        if member not in self.history:
            self.history[member] = []
        self.history[member].append(title)
        return True

    def return_book(self, title):
        book = self.books[title]
        book['checked_out_by'] = None
        book['due_date'] = None
        return True

    def is_overdue(self, title, today):
        book = self.books[title]
        days_late = book['due_date'] - today
        return days_late.days > 0

    def member_history(self, member, _seen=[]):
        _seen.extend(self.history.get(member, []))
        return _seen


def main():
    lib = Library()
    lib.add_book("Dune")
    lib.add_book("Foundation")

    due = date(2026, 7, 25)
    today = date(2026, 7, 18)

    print("Checkout Dune to Alice:", lib.checkout("Dune", "Alice", due))
    print("Checkout Dune to Bob (already out!):", lib.checkout("Dune", "Bob", due))

    print("Is Dune overdue?", lib.is_overdue("Dune", today))

    print("Alice's history:", lib.member_history("Alice"))
    print("Bob's history:", lib.member_history("Bob"))

    print("Return a book nobody checked out:")
    lib.return_book("Foundation")

    print("Checkout a book that doesn't exist:")
    lib.checkout("Neuromancer", "Alice", due)


if __name__ == "__main__":
    main()