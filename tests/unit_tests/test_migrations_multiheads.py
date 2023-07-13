import glob
import os
import re
import pytest
from collections import Counter


def test_alembic_down_revision():
    # Construct the path to the versions directory
    versions_dir = os.path.join('.', 'migrations', 'versions')

    # Get all .py files in versions directory
    all_py_files = glob.glob(os.path.join(versions_dir, "*.py"))

    # Regex pattern for finding down_revision lines in .py files
    down_revision_pattern = re.compile(r'down_revision = \'(\w+)\'')

    down_revisions = []
    file_down_revisions = []

    for file in all_py_files:
        with open(file) as f:
            content = f.read()
            match = down_revision_pattern.search(content)
            if match:
                down_revisions.append(match.group(1))
                file_down_revisions.append((file, match.group(1)))

    counter = Counter(down_revisions)

    duplicates = [item for item, count in counter.items() if count > 1]
    # get the files that have duplicate down revisions
    files_with_duplicates = [file for file, down_revision in file_down_revisions if down_revision in duplicates]

    assert len(duplicates) == 0, f"Duplicate down revisions found in files: {files_with_duplicates} \n this is " \
                                 f"caused because a newer migration might have been added after the migration " \
                                 f"you added. Please fix this by changing the down_revision to the correct one."
