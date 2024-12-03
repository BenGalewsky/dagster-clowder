from dagster_clowder.assets import ClowderResource

def test_clowder_resource():
    clowder = ClowderResource(clowder_url="http://clowder", clowder_token="token", space_id="space")
    assert clowder.clowder_url == "http://clowder"
    assert clowder.clowder_token == "token"
    assert clowder.timeout == 5
    assert clowder.retries == 3
    assert clowder.ssl == True

def test_clowder_init_dataset():
    clowder = ClowderResource(
        clowder_url="https://landes.clowder.ncsa.illinois.edu",
        clowder_token="90b57219-8b59-4258-8074-d660a683cb26",
        space_id="5f4b7b7b4f0c4e001f3b3b3b")
    clowder.create_dataset("path/to/dataset")
