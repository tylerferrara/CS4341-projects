import random
import game
import threading
import ga_alpha_beta_agent as ga

# create specified number of children from two parents
def create_children(parents, num_children):
    print("*****************************************")
    print("         generating offspring")
    print("*****************************************")
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
    # create a non-zero delta
    delta = random.uniform(0.7777777777777777777777, 0.99999999999999999999999)
    # while delta == 0:
    #     delta = random.random()
    
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

    for _ in range(5):
        # randomize the game
        w = random.randint(4, 8)
        h = random.randint(4, 8)
        tokens_to_win = random.randint(3, min(h, h))
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
# RETURN []
#
def play_tournament(w, h, n, l, gene_list):
    # Initialize scores
    scoreboard = Scoreboard(len(gene_list))
    # Play each match in a different thread
    threads = []
    for i in range(0, len(gene_list)-1):
        for j in range(i + 1, len(gene_list)):
            # create a new thread
            args = (scoreboard, w, h, n, l, (i, gene_list[i]), (j, gene_list[j]))
            thread = threading.Thread(target=play_multi_threaded_match, args=args)
            threads.append(thread)
            thread.start()


    # wait for all threads to stop
    for thread in threads:
        thread.join()

    # Calculate and print scores
    scores = scoreboard.get_scores()
    sscores = sorted( ((v,k) for k,v in scores.items()), reverse=True)
    print("\nSCORES:")
    for v,k in sscores:
        print(v,k)
    return sscores



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