from dejavu import Dejavu
from keys import MYSQL_PASS, MYSQL_USER


def fingerprintFile(fileName):
    config = {
        "database": {
            "host": "127.0.0.1",
            "user": MYSQL_USER,
            "passwd": MYSQL_PASS,
            "db": "dejavu",
        },
        "database_type": "mysql",
        "fingerprint_limit": -1
    }

    djv = Dejavu(config)

    djv.fingerprint_file(fileName + ".wav", fileName)


