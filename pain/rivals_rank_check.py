# automatic rank distributor for rivals
#goal : using user input to determine the appropriate ranks each team member can have to be relatively equal in skill level.

Ranks = '''
bronze 
silver 
gold 
platinum 
diamond 
grandmaster 
celestial


'''
new_ranks = []

new_ranks = Ranks.split()
base_ranks = []
count = 0
for i in new_ranks:
    a = [i + " 3", i + " 2", i + " 1"]   
    base_ranks.append(a)
    count += 3
base_ranks = [item for sublist in base_ranks for item in sublist] # flatten the list
base_ranks.append("OAA")
count += 1
#print(base_ranks)
#print(f"Total ranks: {count}")

user_input = input("Enter rank range (e.g., 'bronze 3' to 'gold 1') for tournament: ").lower().strip().split(" to ")

player_ranks = [r.strip() for r in input("Enter player ranks seperated by comma ',': ").lower().split(',')
 ]

rank_range = []
ranks_list = []

for index, rank in enumerate(base_ranks):
    for j in user_input:
        if j == rank:
            rank_range.append(index)
    for g in player_ranks:
        if g == rank:
            ranks_list.append(index)
print(rank_range)
print(ranks_list)

total = 0
for i in ranks_list:
    total += i
if len(rank_range) < 2:
    print("invalid rank range")
else:
    average = total / len(ranks_list)

    average = round(average)

    if average < rank_range[0] or average > rank_range[1]:
        print("out of range change a player")
    else:
        print("in range")