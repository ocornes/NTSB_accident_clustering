import os.path
import gensim
import numpy as np
from gsdmm import MovieGroupProcess
from NTSBUtils import get_docs, get_topics_lists, print_top_words, print_topics, export_model, load_model

LINE = 1  # 1 for 'probable cause', 0 for 'analysis'
OVERWRITE = False
GSDMM_MODEL = "gsdmmFINAL.model"  # leave "" if training
DATASET = "dataset_extended/"
NUMBER_WORDS = 10
ITER = 25
ADDITIONAL_STOPS = ["airplane", "aircraft", "airline", "fly", "reported", "accrued", "common", "unit", "standard",
                    "flown", "faa"]


def generate_model(number_topics=10, model_file=GSDMM_MODEL, verbose=False):
    # fit model or load from file
    if OVERWRITE or not os.path.exists(model_file):
        model = MovieGroupProcess(K=number_topics, alpha=0.1, beta=0.3, n_iters=ITER)

        # fit GSDMM model
        model.fit(docs, vocab_length)

        # save model
        export_model(model, model_file)
    else:
        print(f"[i] Loading model from {model_file}")
        model = load_model(model_file)

    return model


def generate_topics(model, verbose=False):
    # print number of documents per topic
    doc_count = np.array(model.cluster_doc_count)
    if verbose:
        print(f"Number of documents per topic: {doc_count}")

    # Topics sorted by the number of document they are allocated to
    top_index = (-doc_count).argsort()
    if verbose:
        print(f"Most important topics (by number of docs inside): {top_index}")

    # get top words in topics
    if verbose:
        print_top_words(model.cluster_word_distribution, top_index, NUMBER_WORDS)

    # convert to same format as LDA topics
    return get_topics_lists(model.cluster_word_distribution, top_index, NUMBER_WORDS), top_index


def calculate_coherence(topics, metric='u_mass'):
    coherence_model = gensim.models.CoherenceModel(topics=topics,
                                                   dictionary=dictionary,
                                                   corpus=corpus,
                                                   texts=docs,
                                                   coherence=metric)
    return coherence_model.get_coherence()


if __name__ == "__main__":
    # load documents
    docs, docs_ = get_docs(DATASET, line=LINE, additional_stop_words=ADDITIONAL_STOPS)

    # create dictionary
    dictionary = gensim.corpora.Dictionary(docs)
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

    vocab_length = len(dictionary)
    print(f"Size of vocabulary: {vocab_length}")

    # convert to bag-of-words
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    # If particular model specified, run that model
    if GSDMM_MODEL != "":
        # load model
        gsdmm = generate_model(model_file=GSDMM_MODEL)

        # generate topics from model
        topics, indices = generate_topics(gsdmm)
        print("\nTopics:")
        print_topics(topics, indices)

        # Calculate coherence
        coherence = calculate_coherence(topics)
        print(f"The GSDMM model ({len(topics)} topics) has a coherence of: {coherence}")

        doc_idx = 10
        topic_generated, _ = gsdmm.choose_best_label(docs[doc_idx])
        print(f"The document (doc #{doc_idx}):\n{docs_[doc_idx]}Generated Topic: {topic_generated}")

        quit(0)

    # Otherwise, train models for following topic sizes
    Ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 45, 50]
    for number_topics in Ks:
        # generate or load model
        gsdmm = generate_model(number_topics, f"gsdmm{number_topics}.model")

        # generate topics from model
        topics, indices = generate_topics(gsdmm)
        print("\nTopics:")
        print_topics(topics, indices)
        true_topics = '[~' + str(len(topics)) + ']' if number_topics != len(topics) else ''

        # Calculate coherence
        coherence = calculate_coherence(topics)
        print(f"The GSDMM model ({number_topics}{true_topics} topics) has a coherence of: {coherence}")
