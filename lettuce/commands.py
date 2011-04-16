#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2011>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import optparse

import lettuce
from lettuce.core import RunController


def main(args=sys.argv[1:]):
    base_path = os.path.join(os.path.dirname(os.curdir), 'features')
    parser = optparse.OptionParser(
        usage="%prog or type %prog -h (--help) for help",
        version=lettuce.version
    )

    parser.add_option("-v", "--verbosity",
                      dest="verbosity",
                      default=4,
                      help='The verbosity level')

    parser.add_option("-s", "--scenarios",
                      dest="scenarios",
                      default=None,
                      help='Comma separated list of scenarios to run')

    parser.add_option("--failed",
                      action="store_true",
                      dest="only_run_failed",
                      default=False,
                      help='Only re-run tests that failed last time')

    parser.add_option("--syntax",
                      action="store_true",
                      dest="only_syntax_check",
                      default=False,
                      help='Only syntax check, do not actually run any tests (so quick)')

    parser.add_option("--id-file",
                      dest="id_file",
                      default=".lettuceids",
                      help='Filename to keep ids of tests that failed last time, default is .lettuceids, set to None to disable')

    parser.add_option("--with-xunit",
                      dest="enable_xunit",
                      action="store_true",
                      default=False,
                      help='Output JUnit XML test results to a file')

    parser.add_option("--xunit-file",
                      dest="xunit_file",
                      default=None,
                      type="string",
                      help='Write JUnit XML to this file. Defaults to '
                      'lettucetests.xml')

    options, args = parser.parse_args()
    if args:
        base_path = os.path.abspath(args[0])

    try:
        options.verbosity = int(options.verbosity)
    except ValueError:
        pass

    run_controller = RunController(options.id_file, options.only_run_failed, options.only_syntax_check)
    runner = lettuce.Runner(base_path, scenarios=options.scenarios,
                            verbosity=options.verbosity,
                            enable_xunit=options.enable_xunit,
                            xunit_filename=options.xunit_file,
                            run_controller = run_controller)

    result = runner.run()
    if not result or result.steps != result.steps_passed:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
