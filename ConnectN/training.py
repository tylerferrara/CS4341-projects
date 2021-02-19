import random
import genetics as gen

    

# gene_list = [
#     [0, 0, 0, 0, 0],
#     [1, 1, 1, 1, 1],
#     [0.5, 0.5, 0.5, 0.5, 0.5],
#     [0.25, 0.25, 0.25, 0.25, 0.25],
#     [0.75, 0.75, 0.75, 0.75, 0.75],
# ]

random.seed(2)

# should be an even number of individuals
def rand_gene_list(num_genes):
    r = []
    for _ in range(num_genes):
        p = []
        for _ in range(5):
            p.append(random.random())
        r.append(p)
    return r


gene_list = rand_gene_list(8)
best_score = float('-inf')
best_genes = []

try:
    # Quit (Ctrl-C) to stop training
    while True:
        # print gene list
        print("================================================================")
        print("                     current gene_list")
        print("----------------------------------------------------------------")
        for i, gene in enumerate(gene_list):
            print("ID ", i, " -> ",gene)
        print("================================================================")
        # sorted list of tuples [(score, index_from_gene_list)]
        performance = gen.run_multi_tournament(gene_list)
        # store max
        if best_score < performance[0][0]:
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
            next_gen = next_gen + gen.create_children(best_perf_genes, 2)
            # iterate
            gene_idx = gene_idx + 2

        gene_list = next_gen
        
except:
    print("")
    print("==========================")
    print("         FINISHED")
    print("==========================")
    print("highest score: ", best_score)
    print("best genes: ")
    for g in best_genes:
        print(g)
    print("")
