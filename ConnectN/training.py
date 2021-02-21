import random
import game
import threading
import sys
import ga_alpha_beta_agent as ga
from datetime import datetime

# CHANGE THE SEED VALUE!
random.seed(634)


TOURNAMENTS_PER_GEN = 2
GLOBAL_THREADS = []

# create specified number of children from two parents
def create_children(parents, num_children):
    print("-----------> generating offspring")
    children = []
    for _ in range(num_children):
        # decide who is parent1 and parent2
        p1, p2 = parents[0], parents[1]
        if random.randint(0,1) == 0:
            p2, p1 = parents[0], parents[1]
        # split at random point
        split_at = random.randint(1, len(p1)-1)
        child = p1[0:split_at] + p2[split_at:]
        # mutate child
        for i, v in enumerate(child):
            # mutate 25% of the time
            if random.randint(0, 4) == 2:
                print("mutating value ", v)
                child[i] = mutate_float(v)
                print("\t to -> ", child[i])

                
        children.append(child)
    
    return children

# define a mutation to modify a float in range [0,1]
def mutate_float(v):
    if v == 0:
        v = 0.0000000000001
    # create a non-zero delta
    delta = random.uniform(0.6666666666, 1.0)
    while delta == 1.0:
        delta = random.uniform(0.6666666666, 1.0)
    
    if random.randint(0, 1) == 1:
        # multiply (makes v smaller)
        return (delta * v) % 1.0
    else:
        # divide (makes v larger)
        return (delta / v) % 1.0    
    

# returns SORTED list of tupes [(score, index_from_gene_list)]
def run_multi_tournament(gene_list):
    time_limit = 15
    roster = {}

    for _ in range(TOURNAMENTS_PER_GEN):
        # randomize the game
        w = random.randint(4, 10)
        h = random.randint(4, 10)
        tokens_to_win = random.randint(3, min(h, w))
        print(".\n.\n.\n.")
        print("-------- NEW Tournament --------")
        print("Size: ", w, " X ", h)
        print("Winning: ", tokens_to_win, "_in_a_row")
        # play the tournament
        sscores = play_tournament(w, h, tokens_to_win, time_limit, gene_list)
        # keep track of scores
        for r in sscores:
            score = r[0]
            name = r[1]
            if name in roster:
                roster[name] = roster[name] + score
            else:
                roster[name] = score
    
    return sorted( ((v,int(k, base=10)) for k,v in roster.items()), reverse=True)


# Thread safe dictionary to keep track of tournament scores
class Scoreboard():
    def __init__(self, n_ps):
        scores = {}
        for p in range(n_ps):
            scores[str(p)] = 0
        self.scores = scores
        self.lock = threading.Lock()
    
    def add_score(self, key, score):
        with self.lock:
            self.scores[key] = self.scores[key] + score

    def get_scores(self):
        return self.scores

# Play a tournament.
#
# PARAM [int]                 w:  the board width
# PARAM [int]                 h:  the board height
# PARAM [int]                 n:  the number of tokens to line up to win
# PARAM [int]                 l:  the time limit for a move in seconds
# PARAM [list of agent.Agent] ps: the agents in the tournament
# RETURN [list of tuple (int:score, int:gene_list index)]
#
def play_tournament(w, h, n, l, gene_list):
    # Initialize scores
    scoreboard = Scoreboard(len(gene_list))
    # Play each match in a different thread
    GLOBAL_THREADS = []
    for i in range(0, len(gene_list)-1):
        for j in range(i + 1, len(gene_list)):
            # create a new thread
            args = (scoreboard, w, h, n, l, (i, gene_list[i]), (j, gene_list[j]))
            thread = threading.Thread(target=play_multi_threaded_match, args=args)
            GLOBAL_THREADS.append(thread)
            thread.start()


    # wait for all threads to stop
    for thread in GLOBAL_THREADS:
        thread.join()
    

    # Calculate and print scores
    scores = scoreboard.get_scores()
    sscores = sorted( ((v,k) for k,v in scores.items()), reverse=True)
    print("\nSCORES:")
    for v,k in sscores:
        print(v,k)
    return sscores


# Modification of play_match to add multithreading
#
# PARAM [int]         w:  the board width
# PARAM [int]         h:  the board height
# PARAM [int]         n:  the number of tokens to line up to win
# PARAM [int]         l:  the time limit for a move in seconds
# PARAM [tuple (int, gene list)] a: the first agent id and gene list
# PARAM [tuple (int, gene list)] b: the second agent id and gene list
def play_multi_threaded_match(scoreboard, w, h, n, l, a, b):
    # create the agents
    a_agent = ga.GAAlphaBetaAgent(str(a[0]), 5, n, a[1])
    b_agent = ga.GAAlphaBetaAgent(str(b[0]), 5, n, b[1])

    print("starting multi-threaded match")
    (s1, s2) = play_match(w, h, n, l, a_agent, b_agent)
    scoreboard.add_score(str(a[0]), s1)
    scoreboard.add_score(str(b[0]), s2)



# Play a match.
#
# PARAM [int]         w:  the board width
# PARAM [int]         h:  the board height
# PARAM [int]         n:  the number of tokens to line up to win
# PARAM [int]         l:  the time limit for a move in seconds
# PARAM [agent.Agent] p1: the agent for Player 1
# PARAM [agent.Agent] p2: the agent for Player 2
def play_match(w, h, n, l, p1, p2):
    print("  MATCH:", p1.name, "vs.", p2.name)
    # Play the games
    o1 = play_game(w, h, n, l, p1, p2)
    o2 = play_game(w, h, n, l, p2, p1)
    # Calculate scores
    s1 = 0
    s2 = 0
    if o1 == 1:
        s1 = s1 + 1
        s2 = s2 - 1
    elif o1 == 2:
        s1 = s1 - 1
        s2 = s2 + 1
    if o2 == 1:
        s1 = s1 - 1
        s2 = s2 + 1
    elif o2 == 2:
        s1 = s1 + 1
        s2 = s2 - 1
    return (s1, s2)


# Play a single game.
#
# PARAM [int]         w:  the board width
# PARAM [int]         h:  the board height
# PARAM [int]         n:  the number of tokens to line up to win
# PARAM [int]         l:  the time limit for a move in seconds
# PARAM [agent.Agent] p1: the agent for Player 1
# PARAM [agent.Agent] p2: the agent for Player 2
def play_game(w, h, n, l, p1, p2):
    g = game.Game(w,  # width
                  h,  # height
                  n,  # tokens in a row to win
                  p1, # player 1
                  p2) # player 2
    o = g.timed_go(l)
    print("    GAME:", p1.name, "vs.", p2.name, ": ", end='')
    if o == 0:
        print("tie")
    elif o == 1:
        print(p1.name, "won!")
        if (p1.name == "New AI" or p2.name == "New AI") and p1.name != "New AI":
            print("1 - ", p1.name, " 2 - ", p2.name)
            g.board.print_it()
    else:
        print(p2.name, "won!")
        if (p1.name == "New AI" or p2.name == "New AI") and p2.name != "New AI":
            print("1 - ", p1.name, " 2 - ", p2.name)
            g.board.print_it()
    return o
    
# should be an even number of individuals
def rand_gene_list(num_genes):
    r = []
    for _ in range(num_genes):
        p = []
        for _ in range(5):
            p.append(random.random())
        r.append(p)
    return r



# gene_list = rand_gene_list(6)
#
#   SPREAD
#
gene_list = [
    [0.5, 0.5, 0.5, 0.5, 0.5],
    [0.25, 0.25, 0.25, 0.25, 0.25],
    [0.75, 0.75, 0.75, 0.75, 0.75],
    [0.9, 0.2, 0.0001, 0.057, 0.2],
]

#
#
# FROM FILE
#
# gene_list = [
#     [0.26478424425975633,
#     0.178816071472772,
#     0.1627143620522915,
#     0.340475911315279,
#     7.198207202076217e-14],

#     [0.2621994622874513,
#     0.44650040812843694,
#     0.5773872191555337,
#     0.4499724986554245,
#     0.9589804149235308],

#     [0.19107211499409527,
#     0.3209770342820727,
#     0.20857265961971694,
#     0.9970452049139531,
#     0.5369463139609766],

#     [0.22891883854864437,
#     0.09943821131995012,
#     0.8266247142681928,
#     0.46830705500335695,
#     0.38741899424498877],

#     [0.8003325372556609, 0.8268601826296749, 0.25, 0.6950112639600965, 0],

#     [0.8003325372556609, 0.8268601826296749, 0.25, 0.6950112639600965, 0.00000000006],
# ]


# gene_list = [
#  [0.2828269484478088,
#  0.23935434718429693,
#  0.5667751444749664,
#  0.1443564925617226,
#  0.15116989457770513],

#  	[0.050874248080158946,
# 	0.3886001917914304,
# 	0.04628599608344611,
# 	0.1053550559335609,
# 	0.11649273467156096],

#     [0.7052319682422649,
# 	0.43528421616625285,
# 	0.7643120923042259,
# 	0.039710705133870317,
# 	0.2632588094475363],
    
#     [0.3573158378399315,
# 	0.006505743002662411,
# 	0.2178973931077295,
# 	0.7502976987563414,
# 	0.18560570046821137]


# ]



best_score = float('-inf')
best_genes = []

try:

    if len(gene_list) % 2 != 0:
        print("[INVALID] gene_list must have an even number of genes")
        print("exiting...")
        sys.exit(1)

    # Quit (Ctrl-C) to stop training
    while True:
        # print gene list
        print("\n\n================================================================")
        print("                     current gene_list")
        print("----------------------------------------------------------------")
        for i, gene in enumerate(gene_list):
            print("ID ", i, " -> ",gene)
        print("================================================================")
        # sorted list of tuples [(score, index_from_gene_list)]
        performance = run_multi_tournament(gene_list)
        # store max
        if best_score < performance[0][0]:
            if len(best_genes) > 0:
                # beat the best AI to BECOME the best AI
                running = run_multi_tournament([best_genes, gene_list[performance[0][1]]])
                best_score = running[0][0]
                best_genes = gene_list[running[0][1]]
            else:
                best_score = performance[0][0]
                best_genes = gene_list[performance[0][1]]
        # create next gen
        next_gen = []
        gene_idx = 0
        while len(next_gen) < len(gene_list):
            # mate in pairs
            best_perf_genes = [
                gene_list[performance[gene_idx][1]],
                gene_list[performance[gene_idx+1][1]],
            ]
            # create 2 children
            next_gen = next_gen + create_children(best_perf_genes, 2)
            # iterate
            gene_idx = gene_idx + 2

        gene_list = next_gen
        print("\n\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("best_score_so_far: ", best_score)
        print("GRADE (wins/possible_wins): ", (best_score / ((len(gene_list) - 1) * 2)))
        print("Improving? ", best_score == performance[0][0])
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
except KeyboardInterrupt:
    print("\n\nWAITING for threads to stop.....")
    # wait for all threads to stop
    for thread in GLOBAL_THREADS:
        thread.join()

    if len(best_genes) == 0:
        print("\nYou exited too early to make a new generation!")
    else:
        print("\n==========================")
        print("         FINISHED")
        print("==========================")
        print("highest score: ", best_score)
        print("best genes: ")
        for g in best_genes:
            print("\t"+str(g))
        print("")
        # write to file
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f = open("ga_results.txt", "a")
        f.write("\n----> " + dt_string)
        f.write("\nhighest score: " + str(best_score))
        f.write("\nbest genes: ")
        v_names = [
            "TRAP_BONUS",
            "SPEED_TO_WIN",
            "N_IN_A_ROW_SCALAR",
            "DEFENSE_RATIO",
            "MID_SCALAR",
        ]
        for i, v in enumerate(best_genes):
            f.write("\n" + v_names[i] + ": " +str(v))
    
