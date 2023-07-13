import numpy as np
import shutil
import pytest

import lancedb
from superagi.vector_store.lancedb import LanceDB
from superagi.vector_store.document import Document
from superagi.vector_store.embedding.openai import OpenAiEmbedding


@pytest.fixture
def client():
    db = lancedb.connect(".test_lancedb")
    yield db
    shutil.rmtree(".test_lancedb")


@pytest.fixture
def mock_openai_embedding(monkeypatch):
    monkeypatch.setattr(
        OpenAiEmbedding,
        "get_embedding",
        lambda self, text: np.random.random(3).tolist(),
    )


@pytest.fixture
def store(client, mock_openai_embedding):
    yield LanceDB(client, OpenAiEmbedding(api_key="test_api_key"), "text")


@pytest.fixture
def dataset():
    book_titles = [
        "The Great Gatsby",
        "To Kill a Mockingbird",
        "1984",
        "Pride and Prejudice",
        "The Catcher in the Rye",
    ]

    documents = []
    for i, title in enumerate(book_titles):
        author = f"Author {i}"
        description = f"A summary of {title}"
        text_content = f"This is the text for {title}"
        metadata = {"author": author, "description": description}
        document = Document(text_content=text_content, metadata=metadata)

        documents.append(document)

    return documents


@pytest.fixture
def dataset_no_metadata():
    book_titles = [
        "The Lord of the Rings",
        "The Hobbit",
        "The Chronicles of Narnia",
    ]

    documents = []
    for title in book_titles:
        text_content = f"This is the text for {title}"
        document = Document(text_content=text_content)
        documents.append(document)

    return documents


@pytest.mark.parametrize(
    "data, results, table_name",
    [
        ("dataset", (5, 2), "test_table"),
        ("dataset_no_metadata", (3, 0), "test_table_no_metadata"),
    ],
)
def test_add_texts(store, client, data, results, table_name, request):
    dataset = request.getfixturevalue(data)
    count, meta_count = results
    ids = store.add_documents(dataset, table_name=table_name)
    assert len(ids) == count

    tbl = client.open_table(table_name)
    assert len(tbl.to_pandas().columns) - 3 == meta_count
    # Subtracting 3 because of the id, vector, and text columns. The rest
    # should be metadata columns.


@pytest.mark.parametrize(
    "data, search_text, table_name, meta_num",
    [
        ("dataset", "The Great Gatsby", "test_table", 3),
        ("dataset", "1984", "test_table2", 3),
        ("dataset_no_metadata", "The Hobbit", "test_table_no_metadata", 1),
    ],
)
def test_get_matching_text(store, data, search_text, table_name, meta_num, request):
    dataset = request.getfixturevalue(data)
    store.add_documents(dataset, table_name=table_name)
    results = store.get_matching_text(search_text, top_k=2, namespace=table_name)

    assert len(results) == 2
    assert len(results[0].metadata) == meta_num
    # Metadata for dataset with metadata should be 3 (author, desc, text_content)
    # Metadata for dataset without metadata should be 1 (text_content)