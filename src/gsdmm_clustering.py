import os.path
from pickle import dump, load
import gensim
import numpy as np
from gsdmm import MovieGroupProcess
from NTSBUtils import get_docs, get_topics_lists, print_top_words

OVERWRITE = False
GSDMM_MODEL = "gsdmm.model"
DATASET = "dataset_extended/"
NUMBER_TOPICS = 20
NUMBER_WORDS = 10
ITER = 25

if __name__ == "__main__":
    docs = get_docs(DATASET, line=1,
                    additional_stop_words=["pilot"])

    # create dictionary
    dictionary = gensim.corpora.Dictionary(docs)
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

    vocab_length = len(dictionary)
    print(f"Size of vocabulary: {vocab_length}")

    # convert to bag-of-words
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    # fit model or load from file
    if OVERWRITE or not os.path.exists(GSDMM_MODEL):
        gsdmm = MovieGroupProcess(K=NUMBER_TOPICS, alpha=0.1, beta=0.3, n_iters=ITER)

        # fit GSDMM model
        y = gsdmm.fit(docs, vocab_length)

        # export model
        f = open(GSDMM_MODEL, "wb")
        dump(gsdmm, f)
        f.close()
    else:
        print(f"[i] Loading model from {GSDMM_MODEL}")
        f = open(GSDMM_MODEL, "rb")
        gsdmm = load(f)
        f.close()

    # print number of documents per topic
    doc_count = np.array(gsdmm.cluster_doc_count)
    print(f"Number of documents per topic: {doc_count}")

    # Topics sorted by the number of document they are allocated to
    top_index = (-doc_count).argsort()
    print(f"Most important topics (by number of docs inside): {top_index}")

    # get top words in topics
    print_top_words(gsdmm.cluster_word_distribution, top_index, NUMBER_WORDS)

    # convert to same format as LDA topics
    topics = get_topics_lists(gsdmm, top_index, NUMBER_WORDS)
    # print(topics)

    # Calculate coherence
    coherence_model = gensim.models.CoherenceModel(topics=topics,
                                                   dictionary=dictionary,
                                                   corpus=corpus,
                                                   texts=docs,
                                                   coherence='c_v')
    print(f"The GSDMM model has a coherence of: {coherence_model.get_coherence()}")
