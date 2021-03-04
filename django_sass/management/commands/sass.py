from typing import Dict
import os
import sys
import time

from django.core.management.base import BaseCommand
import sass

from django_sass import compile_sass, find_static_scss


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
            "-g",
            dest="g",
            action="store_true",
            help="Build a sourcemap. Only applicable if input is a file, not a directory.",
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
            default=8,
            help="Precision. Defaults to 8",
        )
        parser.add_argument(
            "--watch",
            dest="watch",
            action="store_true",
            default=False,
            help="Watch input path and re-generate css files when scss files are changed.",
        )

    def handle(self, *args, **options) -> None:
        """
        Finds all static paths used by the project, and runs sass
        including those paths.
        """

        # Parse options.
        o_inpath = options["in"][0]
        o_outpath = options["out"][0]
        o_srcmap = options["g"]
        o_precision = options["p"]
        o_style = options["t"]

        # Watch files for changes if specified.
        if options["watch"]:
            try:
                self.stdout.write("Watching...")

                # Track list of files to watch and their modified time.
                watchfiles = {}  # type: Dict[str, float]
                while True:
                    needs_updated = False

                    # Build/update list of ALL scss files in static paths.
                    for fullpath in find_static_scss():
                        prev_mtime = watchfiles.get(fullpath, 0)
                        curr_mtime = os.stat(fullpath).st_mtime
                        if curr_mtime > prev_mtime:
                            needs_updated = True
                            watchfiles.update({fullpath: curr_mtime})

                    # Recompile the sass if needed.
                    if needs_updated:
                        # Catch compile errors to keep the watcher running.
                        try:
                            compile_sass(
                                inpath=o_inpath,
                                outpath=o_outpath,
                                output_style=o_style,
                                precision=o_precision,
                                source_map=o_srcmap,
                            )
                            self.stdout.write(
                                "Updated files at %s" % time.time()
                            )
                        except sass.CompileError as exc:
                            self.stdout.write(str(exc))

                    # Go back to sleep.
                    time.sleep(3)

            except (KeyboardInterrupt, InterruptedError):
                self.stdout.write("Bye.")
                sys.exit(0)

        # Write css.
        self.stdout.write("Writing css...")
        compile_sass(
            inpath=o_inpath,
            outpath=o_outpath,
            output_style=o_style,
            precision=o_precision,
            source_map=o_srcmap,
        )
        self.stdout.write("Done.")
