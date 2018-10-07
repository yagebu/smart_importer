"""Duplicate detector importer decorators."""

import logging

from beancount.ingest import similar

from smart_importer.decorator import ImporterDecorator

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class DuplicateDetector(ImporterDecorator):
    """Class for duplicate detector importer helpers.

    Args:
        comparator: A functor used to establish the similarity of two entries.
        window_days: The number of days (inclusive) before or after to scan the
        entries to classify against.
    """

    def __init__(self, comparator=None, window_days=2):
        super().__init__()
        self.comparator = comparator
        self.window_days = window_days

    def main(self, imported_entries, existing_entries):
        """Add duplicate metadata for imported transactions.

        Args:
            imported_entries: The list of imported entries.
            existing_entries: The list of existing entries as passed to the
                importer.

        Returns:
            A list of entries, modified by this detector.
        """

        duplicate_pairs = similar.find_similar_entries(imported_entries, existing_entries, self.comparator, self.window_days)
        # Add a metadata marker to the extracted entries for duplicates.
        duplicate_set = set(id(entry) for entry, _ in duplicate_pairs)
        mod_entries = []
        for entry in imported_entries:
            if id(entry) in duplicate_set:
                marked_meta = entry.meta.copy()
                marked_meta['__duplicate__'] = True
                entry = entry._replace(meta=marked_meta)
            mod_entries.append(entry)

        return mod_entries
