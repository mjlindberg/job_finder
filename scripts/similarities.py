# Should seperate script for calculating similarities

#Techniques employed:
# - Locality Sensitive Hashing (LSH)
# - Minhashing (using Jaccard similarities)
# - Cosine similarities (soft cosine sim)
# - Levenshtein distances
# - Cluster by similarity


####### Using datasketch - Minhash
from datasketch import MinHash

#dupe: >0.87 (need to try w/o stopwords & spaces)
#try doubling the permutations for better accuracy
#wrap MinHash in LeanMinHash for performance
def jaccard_sim(text1, text2, perm=128):
    #data1 = ['minhash', 'is', 'a', 'probabilistic', 'data', 'structure', 'for',
    #        'estimating', 'the', 'similarity', 'between', 'datasets']
    #data2 = ['minhash', 'is', 'a', 'probability', 'data', 'structure', 'for',
    #        'estimating', 'the', 'similarity', 'between', 'documents']
    m1, m2 = MinHash(num_perm = perm), MinHash(num_perm = perm)
    for t in text1:
        m1.update(t.encode('utf8')) #might not be necessary
    for t in text2:
        m2.update(t.encode('utf8'))
    print("Estimated Jaccard for data1 and data2 is", m1.jaccard(m2))
    s1 = set(text1)
    s2 = set(text2)
    actual_jaccard = float(len(s1.intersection(s2)))/float(len(s1.union(s2)))
    print("Actual Jaccard for data1 and data2 is", actual_jaccard)
    return actual_jaccard
##################################
from datasketch import MinHash, MinHashLSH

#LSH is more optimized for multiple sets rather than making multiple MinHashes.
#ideal for identifying texts over a threshold

def lsh_example(texts, perm = 128, thresh = 0.85):
    #set1 = set(['minhash', 'is', 'a', 'probabilistic', 'data', 'structure', 'for',
    #            'estimating', 'the', 'similarity', 'between', 'datasets'])
    #set2 = set(['minhash', 'is', 'a', 'probability', 'data', 'structure', 'for',
    #            'estimating', 'the', 'similarity', 'between', 'documents'])
    #set3 = set(['minhash', 'is', 'probability', 'data', 'structure', 'for',
    #            'estimating', 'the', 'similarity', 'between', 'documents'])
    #m1 = MinHash(num_perm=128)
    #m2 = MinHash(num_perm=128)
    #m3 = MinHash(num_perm=128)
    mhashes = [MinHash(num_perm = perm) for i in range(len(texts))]
    #for d in set1:
    #    m1.update(d.encode('utf8'))
    #for d in set2:
    #    m2.update(d.encode('utf8'))
    #for d in set3:
    #    m3.update(d.encode('utf8'))
    for text, mhash in enumerate(mhashes):
        [mhash.update(t.encode('utf8')) for t in texts[text]]
    # Create LSH index
    lsh = MinHashLSH(threshold=thresh, num_perm=perm)
    [lsh.insert(f"job_{mhash + 1}", mhashes[mhash]) for mhash in range(len(mhashes)) if mhash > 0]
    result = lsh.query(mhashes[0])
    print(f"Approximate neighbours with Jaccard similarity > {thresh}", result)
#####################################