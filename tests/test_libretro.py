import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('libretro', Path(__file__).parents[1] / 'scripts/libretro.py')
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)


class Images(unittest.TestCase):
    def test_formats(self):
        for data, ext in [(b'\x89PNG\r\n\x1a\n', '.png'), (b'\xff\xd8\xff', '.jpg'), (b'GIF89a', '.gif')]:
            self.assertEqual(lib.ext_of(data), ext)
        with self.assertRaises(ValueError):
            lib.ext_of(b'<html>')

    def test_symlink_chain_and_normalization(self):
        files = {'Named_Boxarts/a.png': '120000', 'Named_Boxarts/b.png': '120000', 'Named_Snaps/é.png': '100644'}
        with patch.object(lib, 'fetch', side_effect=[b'b.png', b'../Named_Snaps/\xc3\xa9.png', b'GIF89a']):
            self.assertEqual(lib.resolve('DOS', 'abc', files, 'Named_Boxarts/a.png'), ('Named_Snaps/é.png', b'GIF89a'))

    def test_cycle_and_escape(self):
        for target in (b'a.png', b'../../outside.png', b'/outside.png'):
            with patch.object(lib, 'fetch', return_value=target), self.assertRaises(ValueError):
                lib.resolve('DOS', 'abc', {'Named_Boxarts/a.png': '120000'}, 'Named_Boxarts/a.png')

    def test_git_tree_uses_null_separators(self):
        tree = b'100644 blob abc\tNamed_Snaps/\xc3\xa9.png\x00120000 blob def\tNamed_Snaps/link.png\x00'
        with tempfile.TemporaryDirectory() as tmp, patch.object(lib, 'CACHE', Path(tmp)), patch.object(lib.subprocess, 'run'), patch.object(lib.subprocess, 'check_output', side_effect=['commit\n', tree]) as output:
            commit, files = lib.index('DOS')
            self.assertEqual(commit, 'commit')
            self.assertEqual(files['Named_Snaps/é.png'], '100644')
            self.assertIn('-rz', output.call_args.args[0])
            self.assertEqual(lib.index('DOS'), (commit, files))

    def test_invalid_repo(self):
        with self.assertRaises(ValueError):
            lib.index('../escape')


if __name__ == '__main__':
    unittest.main()
