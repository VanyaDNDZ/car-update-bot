import imp
import os
import os.path
import unittest


class TestCase(unittest.TestCase):
    def __traverse_directory(self, rootpath):
        skip = rootpath + "/tests"  # Skip files under /tests directory.

        file_count = 0
        for root, dirs, files in os.walk(rootpath):

            if root.startswith(skip):
                continue

            for f in files:
                if os.path.splitext(f)[1] != ".py":
                    # We are only interested in .py files.
                    continue

                filepath = "{}/{}".format(root, f)

                with open(filepath, "r") as f:
                    content = f.read()
                    try:
                        # Make sure the file is compilable i.e. valid python code.
                        compile(content, filepath, "exec")
                        # Make sure the file is loadable.
                        imp.load_source("test_mod", filepath)
                    except Exception as e:
                        self.assertTrue(False, "{} did not pass integrity check. Error: {}".format(filepath, e))

                file_count += 1

        return file_count

    def test_file_integrity(self):
        """Check every single .py file in api and make sure it's loadable."""

        basepath = os.path.join(os.path.pardir, os.path.dirname(__file__))
        basepath = os.path.normpath(basepath)

        file_count = 0
        file_count += self.__traverse_directory(basepath + "/bot")
        file_count += self.__traverse_directory(basepath + "/carinfo")

        print("{} files have been checked for integrity.".format(file_count))
