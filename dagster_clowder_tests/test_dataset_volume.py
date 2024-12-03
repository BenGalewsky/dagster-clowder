from dagster_clowder.definitions import DatasetVolume
def test_dataset_dir():
    dataset = DatasetVolume(directory_path="/Users/bengal1/dev/Clowder/dagster-clowder/data")
    print(list(dataset.scan_leaf_directories()))
    assert dataset.directory_path == "/Users/bengal1/dev/Clowder/dagster-clowder/data"
    # assert dataset.dataset_directories() == ["file1", "file2", "file3"]
