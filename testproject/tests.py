import os
import shutil
import subprocess
import time
import unittest

from django_sass import find_static_paths, find_static_scss


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDjangoSass(unittest.TestCase):

    def setUp(self):
        self.outdir = os.path.join(THIS_DIR, "out")

    def tearDown(self):
        # Clean up output files
        shutil.rmtree(self.outdir, ignore_errors=True)

    def assert_output(self, real_outpath: str):
        # Verify that the output file exists.
        print(real_outpath)
        self.assertTrue(os.path.isfile(real_outpath))

        # Verify that the file contains expected output from all sass files.
        with open(real_outpath, encoding="utf8") as f:
            contents = f.read()
            self.assertTrue("/* Tests: app1/scss/_include.scss */" in contents)
            self.assertTrue("/* Tests: app2/scss/_samedir.scss */" in contents)
            self.assertTrue("/* Tests: app2/scss/subdir/_subdir.scss */" in contents)
            self.assertTrue("/* Tests: app2/scss/test.scss */" in contents)

    def test_find_static_paths(self):
        paths = find_static_paths()
        # Assert that it found both of our apps' static dirs.
        self.assertTrue(os.path.join(THIS_DIR, "app1", "static") in paths)
        self.assertTrue(os.path.join(THIS_DIR, "app2", "static") in paths)

    def test_find_static_sass(self):
        files = find_static_scss()
        # Assert that it found all of our scss files.
        self.assertTrue(
            os.path.join(THIS_DIR, "app1", "static", "app1", "scss", "_include.scss") in files)
        self.assertTrue(
            os.path.join(THIS_DIR, "app2", "static", "app2", "scss", "_samedir.scss") in files)
        self.assertTrue(
            os.path.join(THIS_DIR, "app2", "static", "app2", "scss", "test.scss") in files)
        self.assertTrue(
            os.path.join(THIS_DIR, "app2", "static", "app2", "scss", "subdir", "_subdir.scss")
            in files)

    def test_cli(self):
        # Input and output paths relative to django static dirs.
        inpath = os.path.join("app2", "static", "app2", "scss", "test.scss")
        outpath = os.path.join(self.outdir, "test_file.css")
        # Command to run
        cmd = ["python", "manage.py", "sass", inpath, outpath]
        # Run the management command on testproject.
        proc = subprocess.run(cmd, cwd=THIS_DIR)
        # Verify the process exited cleanly.
        self.assertEqual(proc.returncode, 0)
        # Assert output is correct.
        self.assert_output(outpath)

    def test_cli_dir(self):
        # Input and output paths relative to django static dirs.
        inpath = os.path.join("app2", "static", "app2", "scss")
        outpath = self.outdir
        # Expected output path on filesystem.
        real_outpath = os.path.join(self.outdir, "test.css")
        # Command to run
        cmd = ["python", "manage.py", "sass", inpath, outpath]
        # Run the management command on testproject.
        proc = subprocess.run(cmd, cwd=THIS_DIR)
        # Verify the process exited cleanly.
        self.assertEqual(proc.returncode, 0)
        # Assert output is correct.
        self.assert_output(real_outpath)

    def test_cli_srcmap(self):
        # Input and output paths relative to django static dirs.
        inpath = os.path.join("app2", "static", "app2", "scss", "test.scss")
        outpath = os.path.join(self.outdir, "test.css")
        # Command to run
        cmd = ["python", "manage.py", "sass", "-g", inpath, outpath]
        # Run the management command on testproject.
        proc = subprocess.run(cmd, cwd=THIS_DIR)
        # Verify the process exited cleanly.
        self.assertEqual(proc.returncode, 0)
        # Assert output is correct.
        self.assert_output(outpath)
        self.assertTrue(os.path.isfile(os.path.join(self.outdir, "test.css.map")))

    @unittest.skip("Test needs fixed...")
    def test_cli_watch(self):
        # Input and output paths relative to django static dirs.
        inpath = os.path.join("app2", "static", "app2", "scss", "test.scss")
        outpath = os.path.join(self.outdir, "test.css")
        # Command to run
        cmd = ["python", "manage.py", "sass", "--watch", inpath, outpath]
        # Run the management command on testproject.
        proc = subprocess.Popen(cmd, cwd=THIS_DIR)
        time.sleep(0.5)
        # TODO: This test is not working. Do not know how to intentionally send
        # a KeyboardInterrupt to the subprocess without having unittest/pytest
        # immediately die when it sees the interrupt.
        try:
            proc.send_signal(subprocess.signal.CTRL_C_EVENT)
        except KeyboardInterrupt:
            # We actually want the keyboard interrupt.
            pass
        returncode = proc.wait()
        # Verify the process exited cleanly.
        self.assertEqual(returncode, 0)
        # Assert output is correct.
        self.assert_output(outpath)
