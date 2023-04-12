import os
import shutil
import unittest
import zipfile
from hed.errors import HedFileError
from hed.tools.remodeling.cli.run_remodel_backup import main as back_main
from hed.tools.remodeling.cli.run_remodel_restore import main
from hed.tools.remodeling.backup_manager import BackupManager
from hed.tools.util.io_util import get_file_list


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.file_list = ['top_level.tsv', 'sub1/sub1_events.tsv', 'sub2/sub2_events.tsv', 'sub2/sub2_next_events.tsv']
        cls.test_root_back1 = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../data/remodel_tests/test_root_back1')
        cls.test_zip_back1 = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          '../../../data/remodel_tests/test_root_back1.zip')

        cls.extract_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../data/remodel_tests')

    def setUp(self):
        with zipfile.ZipFile(self.test_zip_back1, 'r') as zip_ref:
            zip_ref.extractall(self.extract_path)

    def tearDown(self):
        shutil.rmtree(self.test_root_back1)

    def test_main_restore(self):
        files1 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertEqual(len(files1), 4, "run_restore starts with the right number of files.")
        shutil.rmtree(os.path.realpath(os.path.join(self.test_root_back1, 'sub1')))
        shutil.rmtree(os.path.realpath(os.path.join(self.test_root_back1, 'sub2')))
        os.remove(os.path.realpath(os.path.join(self.test_root_back1, 'top_level.tsv')))
        files2 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertFalse(files2, "run_restore starts with the right number of files.")
        arg_list = [self.test_root_back1, '-n', 'back1']
        main(arg_list)
        files3 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertEqual(len(files3), len(files1), "run_restore restores all the files after")

    def test_no_backup(self):
        # Test bad data directory
        arg_list = [self.test_root_back1]
        with self.assertRaises(HedFileError) as context:
            main(arg_list=arg_list)
        self.assertEqual(context.exception.args[0], "BackupDoesNotExist")

    def test_restore_alt_loc(self):
        alt_path = os.path.realpath(os.path.join(self.extract_path, 'temp'))
        if os.path.exists(alt_path):
            shutil.rmtree(alt_path)
        self.assertFalse(os.path.exists(alt_path))
        arg_list = [self.test_root_back1, '-n', 'back1', '-x', 'derivatives', '-w', alt_path,
                    '-f', 'events', '-e', '.tsv']
        back_main(arg_list)
        files1 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertEqual(len(files1), 4, "run_restore starts with the right number of files.")
        shutil.rmtree(os.path.realpath(os.path.join(self.test_root_back1, 'sub1')))
        shutil.rmtree(os.path.realpath(os.path.join(self.test_root_back1, 'sub2')))
        os.remove(os.path.realpath(os.path.join(self.test_root_back1, 'top_level.tsv')))
        files2 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertFalse(files2, "run_restore starts with the right number of files.")
        arg_list = [self.test_root_back1, '-n', 'back1', '-w',  alt_path,]
        main(arg_list)
        files3 = get_file_list(self.test_root_back1, exclude_dirs=['derivatives'])
        self.assertEqual(len(files3)+1, len(files1), "run_restore restores all the files after")

        if os.path.exists(alt_path):
           shutil.rmtree(alt_path)


if __name__ == '__main__':
    unittest.main()
