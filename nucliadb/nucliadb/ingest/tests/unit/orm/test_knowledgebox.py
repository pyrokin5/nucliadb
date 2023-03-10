from nucliadb.ingest.orm.knowledgebox import chunker


def test_chunker():
    total_items = 100
    chunk_size = 10
    iterations = 0
    for chunk in chunker(list(range(total_items)), chunk_size):
        assert len(chunk) == chunk_size
        assert chunk == list(
            range(iterations * chunk_size, (iterations * chunk_size) + chunk_size)
        )
        iterations += 1

    assert iterations == total_items / chunk_size

    iterations = 0
    for chunk in chunker([], 2):
        iterations += 1
    assert iterations == 0
