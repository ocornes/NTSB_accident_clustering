import math
from itertools import permutations
import numpy as np
from tqdm import tqdm

from src.NTSBUtils import plot_Ws


class Perm:
    def __init__(self, map):
        self.perms = map

    def __call__(self, n):
        return self.perms[n]

    def __str__(self):
        s = "["
        for i in range(len(self.perms)):
            s += f"{i} -> {self.perms[i]}, "
        return s + "]"


def get_perms(number_topics):
    perms = permutations(range(number_topics))
    return [Perm(p) for p in perms]


def get_As():
    return np.array([[0.7, 0.2, 0.1, 0.0],
                     [0.1, 0.4, 0.4, 0.1],
                     [0.6, 0.3, 0.1, 0.0],
                     [0.0, 0.2, 0.3, 0.5]])


def get_Bs():
    return np.array([[0.2, 0.0, 0.1, 0.7],
                     [0.4, 0.1, 0.4, 0.1],
                     [0.3, 0.0, 0.1, 0.6],
                     [0.2, 0.5, 0.3, 0.0]])


def calculate_Ws(As, Bs):
    n_docs, n_topics = As.shape
    Ws = np.empty((n_topics, n_topics))
    log_Bs = np.log(Bs + 1e-6)
    for i in tqdm(range(n_topics)):
        for j in range(n_topics):
            sum_over_d = 0
            for d in range(n_docs):
                sum_over_d += As[d, i] * log_Bs[d, j]
            Ws[i, j] = sum_over_d
    return Ws


def calculate_kl(p, As, Ws):
    n_docs, n_topics = As.shape
    log_As = np.log(As + 1e-6)
    result = 0
    for i in range(n_topics):
        result -= Ws[i, p(i)]
        for d in range(n_docs):
            result += As[d, i] * log_As[d, i]
    return result / n_docs


if __name__ == '__main__':
    As = get_As()
    Bs = get_Bs()
    _, topics = As.shape
    perms = get_perms(topics)
    print("Calculating Ws...")
    Ws = calculate_Ws(As, Bs)
    print(Ws)

    highest = -math.inf
    optimum_p = None
    print("Going through all permutations...")
    for p in tqdm(perms):
        tmp = 0
        for i in range(topics):
            tmp = tmp + Ws[i, p(i)]
        if tmp > highest:
            highest = tmp
            optimum_p = p

    avg_kl = calculate_kl(optimum_p, As, Ws)

    print(f"Optimum permuation was: {optimum_p}")
    print(f"Highest score was: {highest}")
    print(f"Lowest Average KL-Divergence: {avg_kl}")

    # plot_Ws(Ws)
