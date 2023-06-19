import numpy as np
import pytest

from superagi.vector_store import weaviate
from superagi.vector_store.document import Document
from superagi.vector_store.embedding.openai import OpenAiEmbedding


@pytest.fixture
def client():
    client = weaviate.create_weaviate_client(use_embedded=True)
    yield client
    client.schema.delete_all()


@pytest.fixture
def mock_openai_embedding(monkeypatch):
    monkeypatch.setattr(
        OpenAiEmbedding,
        "get_embedding",
        lambda self, text: np.random.random(3).tolist(),
    )


@pytest.fixture
def store(client, mock_openai_embedding):
    client.schema.delete_all()
    yield weaviate.Weaviate(
        client, OpenAiEmbedding(api_key="test_api_key"), "Test_index", "text"
    )


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
    "data, results",
    [
        ("dataset", (5, 2)),
        ("dataset_no_metadata", (3, 0)),
    ],
)
def test_add_texts(store, data, results, request):
    dataset = request.getfixturevalue(data)
    count, num_metadata = results
    ids = store.add_documents(dataset)
    metadata_fields = store._get_metadata_fields()
    assert len(ids) == count
    assert len(metadata_fields) == num_metadata

    # manual cleanup because you will upload to the same index again
    store.client.schema.delete_all()


def test_get_matching_text(store, dataset):
    store.add_documents(dataset)
    results = store.get_matching_text("The Great Gatsby", top_k=2)
    assert len(results) == 2
    assert results[0] == dataset[0]
