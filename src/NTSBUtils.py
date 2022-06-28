from os import listdir, path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def output_errors(**kwargs):
    # Args
    error_file = kwargs.get("error_file") or ''
    unknown = kwargs.get("unknown") or []

    fd = None
    if error_file != '':
        fd = open(error_file, "w")
        fd.write("<DATA>\n<ROWS>\n")

    # Go through all lists of errors provided
    for error_type, errors in kwargs.items():
        # error_file is not a list, unknown is handled separately
        if error_type == "error_file" or error_type == "unknown":
            continue
        if len(errors) > 0:
            print(f"[i] The following event_ids were {error_type}:")
            for failed_id in errors:
                print(f"\t{failed_id}")
                id_to_file(fd, failed_id, error_type)

    if len(unknown) > 0:
        print("[i] The following event_ids failed for unknown reasons:")
        for failed_id, e in unknown:
            print(f"\t{failed_id}, reason: {e}")
            id_to_file(fd, failed_id, 'unknown', e)

    if fd is not None:
        fd.write("</ROWS>\n</DATA>\n")
        fd.close()


def id_to_file(fd, failed_id, reason, additional=''):
    if fd is not None:
        if additional != '':
            reason = f"{reason}, ({additional})"
        fd.write(f"<ROW EventId=\"{failed_id}\" Reason=\"{reason}\"/>\n")


DEAD_TOKENS = ['(C)', '(F)', '(S)']


def parse_findings(findings):
    result = []
    for line in findings:
        colon = line.rfind(':')
        dot = line.rfind('.')
        if colon != -1:
            result.append(replace_dead(line[colon + 1:]).strip())
        elif dot != -1:
            result.append(replace_dead(line[dot + 1:]).strip())

    return result


def replace_dead(a):
    for tok in DEAD_TOKENS:
        a = a.replace(tok, ' ')
    return a


def get_docs(dir, line=0, additional_stop_words=[]):
    if not path.isdir(dir):
        print(f"[!] Directory '{dir}' could not be found")
        return []

    # get list of stopwords
    stops = stopwords.words('english')

    docs = []
    for f in listdir(dir):
        fd = open(dir + f)
        doc = fd.readlines()[line]
        doc = [word for word in word_tokenize(doc.lower()) if
               word.isalnum() and word not in stops and word not in additional_stop_words]
        docs.append(doc)
        fd.close()
    return docs


def get_topics_lists(model, top_clusters, n_words):
    topics = []
    for cluster in top_clusters:
        sorted_dict = sorted(model.cluster_word_distribution[cluster].items(),
                             key=lambda k: k[1], reverse=True)[:n_words]
        topics.append([k for (k, v) in sorted_dict])
    return topics


def print_top_words(cluster_word_distribution, top_cluster, number_words):
    for cluster in top_cluster:
        sort_dicts = sorted(cluster_word_distribution[cluster].items(), key=lambda k: k[1], reverse=True)[:number_words]
        print(f"Topic {cluster}: {sort_dicts}")
