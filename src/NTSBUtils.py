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


DEAD_TOKENS = ['- ', '(C)', '(F)', '(S)']


def parse_findings(findings):
    result = ''
    for line in findings:
        colon = line.rfind(':')
        dot = line.rfind('.')
        if colon != -1:
            result += line[colon + 2:]
        elif dot != -1:
            result += line[dot + 2:]

    for tok in DEAD_TOKENS:
        result = result.replace(tok, '')

    return result.lower()
