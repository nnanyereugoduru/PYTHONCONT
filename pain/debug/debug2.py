'''Dev note (left in a comment by the previous dev):

Quick note before you dig in — this is the room booking system I started, pushed it a bit before I meant to. Mostly worked in my basic testing but a few things have been bugging me and I never got around to verifying:

The double-booking check has felt finicky — I have a nagging feeling I got some boundary logic backwards somewhere, but my test cases kept passing so ¯\_(ツ)_/¯
Something about the attendees list feels off when I don't pass one explicitly — like it's remembering stuff between bookings? Probably me being paranoid.
Tried cancelling something in a room nobody had touched yet and it blew up ugly. Didn't chase it down.
cancel_by_attendee seems to sometimes leave stuff behind when a person has multiple bookings in the same room — only caught it by accident.

Didn't get real tests written, sorry. Good luck.'''

class RoomScheduler:
    def __init__(self):
        self.bookings = {}  # room -> list of booking dicts

    def book(self, room, start, end, title, attendees=[]):
        if room not in self.bookings:
            self.bookings[room] = []

        if self.is_available(room, start, end):
            self.bookings[room].append({
                'start': start,
                'end': end,
                'title': title,
                'attendees': attendees
            })
            return True
        else:
            return False

    def is_available(self, room, start, end):
        for b in self.bookings.get(room, []):
            if start >= b['end'] or end <= b['start']:
                return False
        return True

    def cancel(self, room, start):
        if room in self.bookings:
            for b in self.bookings[room]:
                if b['start'] == start:
                    self.bookings[room].remove(b)
                    return True
            return False
        else:
            print('invalid')

    def cancel_by_attendee(self, name):
        removed = 0
        for room, blist in self.bookings.items():
            for b in blist:
                if name in b['attendees']:
                    blist.remove(b)
                    removed += 1
        return removed

    def daily_schedule(self, room):
        return sorted(self.bookings.get(room, []), key=lambda b: b['start'])
    
    # first thing I did so I can know the actually save 
    def printall(self):
        for rooms in self.bookings.items():
            print(rooms)

def main():
    sched = RoomScheduler()

    sched.book("Falcon", 9, 10, "Standup")
    sched.printall()
    sched.book("Falcon", 10, 11, "Design Review")
    sched.printall()
    sched.book("Falcon", 13, 14, "1:1", attendees=["Sam"])
    sched.printall()
    sched.book("Falcon", 14, 15, "Retro", attendees=["Sam", "Jo"])
    sched.printall() #found the problem of the program not updating 

    print("Falcon schedule:")
    for b in sched.daily_schedule("Falcon"):
        print(f"  {b['start']}-{b['end']}: {b['title']} ({b['attendees']})")

    print("\nTrying to book 10:30-11:30 (should conflict with Design Review)...")
    ok = sched.book("Falcon", 10.5, 11.5, "Sneaky Meeting")
    print("Booked?", ok)

    print("\nCancelling a booking in an empty room...")
    sched.cancel("Osprey", 9)

    print("\nCancelling all of Sam's meetings...")
    removed = sched.cancel_by_attendee("Sam")
    print("Removed:", removed)
    print("Falcon schedule after:")
    for b in sched.daily_schedule("Falcon"):
        print(f"  {b['start']}-{b['end']}: {b['title']} ({b['attendees']})")


if __name__ == "__main__":
    main()