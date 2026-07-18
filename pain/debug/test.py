'''blist = ['A', 'B', 'C']

blist2 = blist
a = list(blist)
blist.remove('A')
print(a)
print(blist2)  '''
 # what does this show?

def book(attendees=[]):
    attendees.append("Alice")
    print(attendees)

book()
book()
book()