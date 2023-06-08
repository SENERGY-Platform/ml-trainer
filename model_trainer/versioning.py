def get_commit(path_to_commit_file):
    try:
        with open(path_to_commit_file) as version_file:
            version = version_file.readline()
            return version
    except FileNotFoundError:
        return "no_commit_file_found"