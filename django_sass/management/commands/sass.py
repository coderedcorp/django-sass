import os
import sys
import time
from django.core.management.base import BaseCommand
from django.contrib.staticfiles.finders import get_finders
import sass


class Command(BaseCommand):
    help = "Runs libsass including all paths from STATICFILES_FINDERS."

    def add_arguments(self, parser):
        parser.add_argument(
            "in",
            type=str,
            nargs="+",
            help="An scss file, or directory containing scss files",
        )
        parser.add_argument(
            "out",
            type=str,
            nargs="+",
            help="A file or directory in which to output transpiled css",
        )
        parser.add_argument(
            "-t",
            type=str,
            dest="t",
            default="expanded",
            help="Output type. One of 'expanded', 'nested', 'compact', 'compressed'",
        )
        parser.add_argument(
            "-p",
            type=int,
            dest="p",
            default=5,
            help="Precision. Defaults to 5 (Bootstrap requires 8)",
        )
        parser.add_argument(
            "--watch",
            dest="watch",
            action="store_true",
            default=False,
            help="Watch input path and re-generate css files when scss files are changed.",
        )

    def compile_sass(self, outfile, **kwargs):
        rval = sass.compile(**kwargs)
        # sass.compile() will return None of used with dirname.
        # If used with filename, it will return a string of file contents.
        if rval and outfile:
            # Write the outputted css to file
            file = open(outfile, "w")
            file.write(rval)
            file.close()

    def handle(self, *args, **options):
        """
        Finds all static paths used by the project, and runs sass
        including those paths.
        """
        found_paths = []
        for finder in get_finders():
            if hasattr(finder, "storages"):
                for appname in finder.storages:
                    if hasattr(finder.storages[appname], "location"):
                        abspath = finder.storages[appname].location
                        found_paths.append(abspath)

        sassargs = {"output_style": options["t"], "precision": options["p"]}
        inpath = options["in"][0]
        outpath = options["out"][0]
        outfile = None

        if found_paths:
            sassargs.update({"include_paths": found_paths})

        if os.path.isdir(inpath):
            # assume outpath is also a dir, or make it
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            if os.path.isdir(outpath):
                sassargs.update({"dirname": (inpath, outpath)})
            else:
                raise NotADirectoryError("Output path must also be a directory when input path is a directory.")

        if os.path.isfile(inpath):
            sassargs.update({"filename": inpath})
            if os.path.isdir(outpath):
                outfile = os.path.join(
                    outpath, os.path.basename(inpath.replace(".scss", ".css"))
                )
            else:
                outfile = outpath

         # Watch files for changes if specified
        if options["watch"]:
            try:
                self.stdout.write("Watching...")
                watchfiles = {}
                while True:
                    needs_updated = False

                    # Build/update list of ALL scss files in static paths.
                    for finder in get_finders():
                        for path, storage in finder.list([]):
                            if path.endswith(".scss"):
                                fullpath = finder.find(path)
                                prev_mtime = watchfiles.get(fullpath, 0)
                                curr_mtime = os.stat(fullpath).st_mtime
                                if curr_mtime > prev_mtime:
                                    needs_updated = True
                                    watchfiles.update({fullpath: curr_mtime})

                    # Recompile the sass if needed
                    if needs_updated:
                        # Catch compile errors to keep the watcher running.
                        try:
                            self.compile_sass(outfile, **sassargs)
                            self.stdout.write("Updated files at %s" % time.time())
                        except sass.CompileError as exc:
                            self.stdout.write(str(exc))

                    # Go back to sleep
                    time.sleep(3)

            except KeyboardInterrupt:
                self.stdout.write("Bye.")
                sys.exit(0)

        # Write css
        self.stdout.write("Writing css...")
        self.compile_sass(outfile, **sassargs)
        self.stdout.write("Done.")
