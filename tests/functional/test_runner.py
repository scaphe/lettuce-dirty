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
import lettuce

from StringIO import StringIO
from os.path import dirname, join, abspath
from nose.tools import assert_equals, with_setup, assert_raises
from lettuce.fs import FeatureLoader
from lettuce.core import Feature, fs, StepDefinition, RunController, ScenarioResultSummary
from lettuce.terrain import world
from lettuce import Runner, step

from tests.asserts import assert_lines
from tests.asserts import assert_stderr
from tests.asserts import prepare_stderr
from tests.asserts import prepare_stdout
from tests.asserts import assert_stderr_lines
from tests.asserts import assert_stdout_lines
from tests.asserts import assert_stderr_lines_with_traceback
from tests.asserts import assert_stdout_lines_with_traceback

current_dir = abspath(dirname(__file__))
lettuce_dir = abspath(dirname(lettuce.__file__))
ojoin = lambda *x: join(current_dir, 'output_features', *x)
sjoin = lambda *x: join(current_dir, 'syntax_features', *x)
fjoin = lambda *x: join(current_dir, 'failed_features', *x)
tjoin = lambda *x: join(current_dir, 'tag_features', *x)
lettuce_path = lambda *x: fs.relpath(join(lettuce_dir, *x))

call_line = StepDefinition.__call__.im_func.func_code.co_firstlineno + 5

def feature_name(name):
    return join(abspath(dirname(__file__)), 'output_features', name, "%s.feature" % name)

def syntax_feature_name(name):
    return sjoin(name, "%s.feature" % name)

def failed_feature_name(name):
    return fjoin(name, "%s.feature" % name)

def tag_feature_name(name):
    return tjoin(name, "%s.feature" % name)

@with_setup(prepare_stderr)
def test_try_to_import_terrain():
    "Runner tries to import terrain, but has a nice output when it fail"
    sandbox_path = ojoin('..', 'sandbox')
    original_path = abspath(".")
    os.chdir(sandbox_path)

    try:
        import lettuce
        reload(lettuce)
        raise AssertionError('The runner should raise ImportError !')
    except SystemExit:
        assert_stderr_lines_with_traceback(
            'Lettuce has tried to load the conventional environment module ' \
            '"terrain"\nbut it has errors, check its contents and ' \
            'try to run lettuce again.\n\nOriginal traceback below:\n\n' \
            "Traceback (most recent call last):\n"
            '  File "%(lettuce_core_file)s", line 44, in <module>\n'
            '    terrain = fs.FileSystem._import("terrain")\n' \
            '  File "%(lettuce_fs_file)s", line 63, in _import\n' \
            '    module = imp.load_module(name, fp, pathname, description)\n' \
            '  File "%(terrain_file)s", line 18\n' \
            '    it is here just to cause a syntax error\n' \
            "                  ^\n" \
            'SyntaxError: invalid syntax\n' % {
                'lettuce_core_file': abspath(join(lettuce_dir, '__init__.py')),
                'lettuce_fs_file': abspath(join(lettuce_dir, 'fs.py')),
                'terrain_file': abspath(lettuce_path('..', 'tests', 'functional', 'sandbox', 'terrain.py')),
            }
        )

    finally:
        os.chdir(original_path)

def test_feature_representation_without_colors():
    "Feature represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_lines(
        feature.represented(),
        "Feature: Addition                                      # tests/functional/simple_features/1st_feature_dir/some.feature:5\n"
        "  In order to avoid silly mistakes                     # tests/functional/simple_features/1st_feature_dir/some.feature:6\n"
        "  As a math idiot                                      # tests/functional/simple_features/1st_feature_dir/some.feature:7\n"
        "  I want to be told the sum of two numbers             # tests/functional/simple_features/1st_feature_dir/some.feature:8\n"
    )

def test_scenario_outline_representation_without_colors():
    "Scenario Outline represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario Outline: Add two numbers                    # tests/functional/simple_features/1st_feature_dir/some.feature:10\n"
    )

def test_scenario_representation_without_colors():
    "Scenario represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6\n"
    )

def test_undefined_step_represent_string():
    "Undefined step represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    assert_equals(
        step.represent_string(step.sentence),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/first.feature:7\n"
    )

    assert_equals(
        step.represent_string("foo bar"),
        "    foo bar                              # tests/functional/output_features/runner_features/first.feature:7\n"
    )

def test_defined_step_represent_string():
    "Defined step represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')
    feature_dir = ojoin('runner_features')
    loader = FeatureLoader(feature_dir)
    world._output = StringIO()
    world._is_colored = False
    loader.find_and_load_step_definitions()

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    step.run(True)

    assert_equals(
        step.represent_string(step.sentence),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless():
    "Testing the colorless output of a successful feature"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'runner_features'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Feature: Dumb feature                    # tests/functional/output_features/runner_features/first.feature:1\n"
        "  In order to test success               # tests/functional/output_features/runner_features/first.feature:2\n"
        "  As a programmer                        # tests/functional/output_features/runner_features/first.feature:3\n"
        "  I want to see that the output is green # tests/functional/output_features/runner_features/first.feature:4\n"
        "\n"
        "  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6\n"
        "    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6\n"
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "1 step (1 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless():
    "A feature with two scenarios should separate the two scenarios with a new line (in colorless mode)."

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_scenarios'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Feature: Dumb feature                    # tests/functional/output_features/many_successful_scenarios/first.feature:1\n"
        "  In order to test success               # tests/functional/output_features/many_successful_scenarios/first.feature:2\n"
        "  As a programmer                        # tests/functional/output_features/many_successful_scenarios/first.feature:3\n"
        "  I want to see that the output is green # tests/functional/output_features/many_successful_scenarios/first.feature:4\n"
        "\n"
        "  Scenario: Do nothing                   # tests/functional/output_features/many_successful_scenarios/first.feature:6\n"
        "    Given I do nothing                   # tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\n"
        "\n"
        "  Scenario: Do nothing (again)           # tests/functional/output_features/many_successful_scenarios/first.feature:9\n"
        "    Given I do nothing (again)           # tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful():
    "Testing the output of a successful feature"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'runner_features'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        "\n" \
        "\033[1;37mFeature: Dumb feature                    \033[1;30m# tests/functional/output_features/runner_features/first.feature:1\033[0m\n" \
        "\033[1;37m  In order to test success               \033[1;30m# tests/functional/output_features/runner_features/first.feature:2\033[0m\n" \
        "\033[1;37m  As a programmer                        \033[1;30m# tests/functional/output_features/runner_features/first.feature:3\033[0m\n" \
        "\033[1;37m  I want to see that the output is green \033[1;30m# tests/functional/output_features/runner_features/first.feature:4\033[0m\n" \
        "\n" \
        "\033[1;37m  Scenario: Do nothing                   \033[1;30m# tests/functional/output_features/runner_features/first.feature:6\033[0m\n" \
        "\033[1;30m    Given I do nothing                   \033[1;30m# tests/functional/output_features/runner_features/dumb_steps.py:6\033[0m\n" \
        "\033[A\033[1;32m    Given I do nothing                   \033[1;30m# tests/functional/output_features/runner_features/dumb_steps.py:6\033[0m\n" \
        "\n" \
        "\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 scenario (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 step (\033[1;32m1 passed\033[1;37m)\033[0m\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful_newline():
    "A feature with two scenarios should separate the two scenarios with a new line (in color mode)."

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_scenarios'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        "\n" \
        "\033[1;37mFeature: Dumb feature                    \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:1\033[0m\n" \
        "\033[1;37m  In order to test success               \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:2\033[0m\n" \
        "\033[1;37m  As a programmer                        \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:3\033[0m\n" \
        "\033[1;37m  I want to see that the output is green \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:4\033[0m\n" \
        "\n" \
        "\033[1;37m  Scenario: Do nothing                   \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:6\033[0m\n" \
        "\033[1;30m    Given I do nothing                   \033[1;30m# tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\033[0m\n" \
        "\033[A\033[1;32m    Given I do nothing                   \033[1;30m# tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\033[0m\n" \
        "\n" \
        "\033[1;37m  Scenario: Do nothing (again)           \033[1;30m# tests/functional/output_features/many_successful_scenarios/first.feature:9\033[0m\n" \
        "\033[1;30m    Given I do nothing (again)           \033[1;30m# tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\033[0m\n" \
        "\033[A\033[1;32m    Given I do nothing (again)           \033[1;30m# tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\033[0m\n" \
        "\n" \
        "\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m2 scenarios (\033[1;32m2 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m2 steps (\033[1;32m2 passed\033[1;37m)\033[0m\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless_many_features():
    "Testing the output of many successful features"
    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_features'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Feature: First feature, of many              # tests/functional/output_features/many_successful_features/one.feature:1\n"
        "  In order to make lettuce more robust       # tests/functional/output_features/many_successful_features/one.feature:2\n"
        "  As a programmer                            # tests/functional/output_features/many_successful_features/one.feature:3\n"
        "  I want to test its output on many features # tests/functional/output_features/many_successful_features/one.feature:4\n"
        "\n"
        "  Scenario: Do nothing                       # tests/functional/output_features/many_successful_features/one.feature:6\n"
        "    Given I do nothing                       # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes          # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "Feature: Second feature, of many    # tests/functional/output_features/many_successful_features/two.feature:1\n"
        "  I just want to see it green :)    # tests/functional/output_features/many_successful_features/two.feature:2\n"
        "\n"
        "  Scenario: Do nothing              # tests/functional/output_features/many_successful_features/two.feature:4\n"
        "    Given I do nothing              # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "2 features (2 passed)\n"
        "2 scenarios (2 passed)\n"
        "4 steps (4 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful_many_features():
    "Testing the colorful output of many successful features"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_features'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        "\n"
        "\033[1;37mFeature: First feature, of many              \033[1;30m# tests/functional/output_features/many_successful_features/one.feature:1\033[0m\n"
        "\033[1;37m  In order to make lettuce more robust       \033[1;30m# tests/functional/output_features/many_successful_features/one.feature:2\033[0m\n"
        "\033[1;37m  As a programmer                            \033[1;30m# tests/functional/output_features/many_successful_features/one.feature:3\033[0m\n"
        "\033[1;37m  I want to test its output on many features \033[1;30m# tests/functional/output_features/many_successful_features/one.feature:4\033[0m\n"
        "\n"
        "\033[1;37m  Scenario: Do nothing                       \033[1;30m# tests/functional/output_features/many_successful_features/one.feature:6\033[0m\n"
        "\033[1;30m    Given I do nothing                       \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:6\033[0m\n"
        "\033[A\033[1;32m    Given I do nothing                       \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:6\033[0m\n"
        "\033[1;30m    Then I see that the test passes          \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:8\033[0m\n"
        "\033[A\033[1;32m    Then I see that the test passes          \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:8\033[0m\n"
        "\n"
        "\033[1;37mFeature: Second feature, of many    \033[1;30m# tests/functional/output_features/many_successful_features/two.feature:1\033[0m\n"
        "\033[1;37m  I just want to see it green :)    \033[1;30m# tests/functional/output_features/many_successful_features/two.feature:2\033[0m\n"
        "\n"
        "\033[1;37m  Scenario: Do nothing              \033[1;30m# tests/functional/output_features/many_successful_features/two.feature:4\033[0m\n"
        "\033[1;30m    Given I do nothing              \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:6\033[0m\n"
        "\033[A\033[1;32m    Given I do nothing              \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:6\033[0m\n"
        "\033[1;30m    Then I see that the test passes \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:8\033[0m\n"
        "\033[A\033[1;32m    Then I see that the test passes \033[1;30m# tests/functional/output_features/many_successful_features/dumb_steps.py:8\033[0m\n"
        "\n"
        "\033[1;37m2 features (\033[1;32m2 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m2 scenarios (\033[1;32m2 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m4 steps (\033[1;32m4 passed\033[1;37m)\033[0m\n"
    )

@with_setup(prepare_stdout)
def test_output_when_could_not_find_features():
    "Testing the colorful output of many successful features"

    path = fs.relpath(join(abspath(dirname(__file__)), 'unexistent-folder'))
    runner = Runner(path, verbosity=4)
    runner.run()

    assert_stdout_lines(
        '\033[1;31mOops!\033[0m\n'
        '\033[1;37mcould not find features at \033[1;33m./%s\033[0m\n' % path
    )

@with_setup(prepare_stdout)
def test_output_when_could_not_find_features_colorless():
    "Testing the colorful output of many successful features colorless"

    path = fs.relpath(join(abspath(dirname(__file__)), 'unexistent-folder'))
    runner = Runner(path, verbosity=3)
    runner.run()

    assert_stdout_lines(
        'Oops!\n'
        'could not find features at ./%s\n' % path
    )

@with_setup(prepare_stdout)
def test_output_when_could_not_find_features_verbosity_level_2():
    "Testing the colorful output of many successful features colorless"

    path = fs.relpath(join(abspath(dirname(__file__)), 'unexistent-folder'))
    runner = Runner(path, verbosity=2)
    runner.run()

    assert_stdout_lines(
        'Oops!\n'
        'could not find features at ./%s\n' % path
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless_with_table():
    "Testing the colorless output of success with table"

    runner = Runner(feature_name('success_table'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        '\n'
        'Feature: Table Success           # tests/functional/output_features/success_table/success_table.feature:1\n'
        '\n'
        '  Scenario: Add two numbers      # tests/functional/output_features/success_table/success_table.feature:2\n'
        '    Given I have 0 bucks         # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        '    And that I have these items: # tests/functional/output_features/success_table/success_table_steps.py:32\n'
        '      | name    | price  |\n'
        '      | Porsche | 200000 |\n'
        '      | Ferrari | 400000 |\n'
        '    When I sell the "Ferrari"    # tests/functional/output_features/success_table/success_table_steps.py:42\n'
        '    Then I have 400000 bucks     # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        '    And my garage contains:      # tests/functional/output_features/success_table/success_table_steps.py:47\n'
        '      | name    | price  |\n'
        '      | Porsche | 200000 |\n'
        '\n'
        '1 feature (1 passed)\n'
        '1 scenario (1 passed)\n'
        '5 steps (5 passed)\n'
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful_with_table():
    "Testing the colorful output of success with table"

    runner = Runner(feature_name('success_table'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        '\n'
        '\033[1;37mFeature: Table Success           \033[1;30m# tests/functional/output_features/success_table/success_table.feature:1\033[0m\n'
        '\n'
        '\033[1;37m  Scenario: Add two numbers      \033[1;30m# tests/functional/output_features/success_table/success_table.feature:2\033[0m\n'
        '\033[1;30m    Given I have 0 bucks         \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:28\033[0m\n'
        '\033[A\033[1;32m    Given I have 0 bucks         \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:28\033[0m\n'
        '\033[1;30m    And that I have these items: \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:32\033[0m\n'
        '\033[1;30m     \033[1;37m |\033[1;30m name   \033[1;37m |\033[1;30m price \033[1;37m |\033[1;30m\033[0m\n'
        '\033[1;30m     \033[1;37m |\033[1;30m Porsche\033[1;37m |\033[1;30m 200000\033[1;37m |\033[1;30m\033[0m\n'
        '\033[1;30m     \033[1;37m |\033[1;30m Ferrari\033[1;37m |\033[1;30m 400000\033[1;37m |\033[1;30m\033[0m\n'
        '\033[A\033[A\033[A\033[A\033[1;32m    And that I have these items: \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:32\033[0m\n'
        '\033[1;32m     \033[1;37m |\033[1;32m name   \033[1;37m |\033[1;32m price \033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m     \033[1;37m |\033[1;32m Porsche\033[1;37m |\033[1;32m 200000\033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m     \033[1;37m |\033[1;32m Ferrari\033[1;37m |\033[1;32m 400000\033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;30m    When I sell the "Ferrari"    \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:42\033[0m\n'
        '\033[A\033[1;32m    When I sell the "Ferrari"    \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:42\033[0m\n'
        '\033[1;30m    Then I have 400000 bucks     \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:28\033[0m\n'
        '\033[A\033[1;32m    Then I have 400000 bucks     \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:28\033[0m\n'
        '\033[1;30m    And my garage contains:      \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:47\033[0m\n'
        '\033[1;30m     \033[1;37m |\033[1;30m name   \033[1;37m |\033[1;30m price \033[1;37m |\033[1;30m\033[0m\n'
        '\033[1;30m     \033[1;37m |\033[1;30m Porsche\033[1;37m |\033[1;30m 200000\033[1;37m |\033[1;30m\033[0m\n'
        '\033[A\033[A\033[A\033[1;32m    And my garage contains:      \033[1;30m# tests/functional/output_features/success_table/success_table_steps.py:47\033[0m\n'
        '\033[1;32m     \033[1;37m |\033[1;32m name   \033[1;37m |\033[1;32m price \033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m     \033[1;37m |\033[1;32m Porsche\033[1;37m |\033[1;32m 200000\033[1;37m |\033[1;32m\033[0m\n'
        '\n'
        "\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 scenario (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m5 steps (\033[1;32m5 passed\033[1;37m)\033[0m\n"
    )

@with_setup(prepare_stdout)
def test_output_with_failed_colorless_with_table():
    "Testing the colorless output of failed with table"

    runner = Runner(feature_name('failed_table'), verbosity=3)
    runner.run()

    assert_stdout_lines_with_traceback(
        "\n"
        "Feature: Table Fail                           # tests/functional/output_features/failed_table/failed_table.feature:1\n"
        "\n"
        "  Scenario: See it fail                       # tests/functional/output_features/failed_table/failed_table.feature:2\n"
        "    Given I have a dumb step that passes      # tests/functional/output_features/failed_table/failed_table_steps.py:20\n"
        "    And this one fails                        # tests/functional/output_features/failed_table/failed_table_steps.py:24\n"
        "    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 25, in tof\n'
        "        assert False\n"
        "    AssertionError\n"
        "    Then this one will be skipped             # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one will be skipped              # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one does not even has definition # tests/functional/output_features/failed_table/failed_table.feature:12 (undefined)\n"
        "\n"
        "1 feature (0 passed)\n"
        "1 scenario (1 failed, 0 passed)\n"
        "5 steps (1 failed, 2 skipped, 1 undefined, 1 passed)\n"
        "\n"
        "You can implement step definitions for undefined steps with these snippets:\n"
        "\n"
        "# -*- coding: utf-8 -*-\n"
        "from lettuce import step\n"
        "\n"
        "@step(u'And this one does not even has definition')\n"
        "def and_this_one_does_not_even_has_definition(step):\n"
        "    assert False, 'This step must be implemented'\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_failed_colorful_with_table():
    "Testing the colorful output of failed with table"

    runner = Runner(feature_name('failed_table'), verbosity=4)
    runner.run()

    assert_stdout_lines_with_traceback(
        "\n"
        "\033[1;37mFeature: Table Fail                           \033[1;30m# tests/functional/output_features/failed_table/failed_table.feature:1\033[0m\n"
        "\n"
        "\033[1;37m  Scenario: See it fail                       \033[1;30m# tests/functional/output_features/failed_table/failed_table.feature:2\033[0m\n"
        "\033[1;30m    Given I have a dumb step that passes      \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:20\033[0m\n"
        "\033[A\033[1;32m    Given I have a dumb step that passes      \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:20\033[0m\n"
        "\033[1;30m    And this one fails                        \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:24\033[0m\n"
        "\033[A\033[0;31m    And this one fails                        \033[1;41;33m# tests/functional/output_features/failed_table/failed_table_steps.py:24\033[0m\n"
        "\033[1;31m    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 25, in tof\n'
        "        assert False\n"
        "    AssertionError\033[0m\n"
        "\033[1;30m    Then this one will be skipped             \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:28\033[0m\n"
        "\033[A\033[0;36m    Then this one will be skipped             \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:28\033[0m\n"
        "\033[1;30m    And this one will be skipped              \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:28\033[0m\n"
        "\033[A\033[0;36m    And this one will be skipped              \033[1;30m# tests/functional/output_features/failed_table/failed_table_steps.py:28\033[0m\n"
        "\033[0;33m    And this one does not even has definition \033[1;30m# tests/functional/output_features/failed_table/failed_table.feature:12\033[0m\n"
        "\n"
        "\033[1;37m1 feature (\033[0;31m0 passed\033[1;37m)\033[0m\n"
        "\033[1;37m1 scenario (\033[0;31m0 passed\033[1;37m)\033[0m\n"
        "\033[1;37m5 steps (\033[0;31m1 failed\033[1;37m, \033[0;36m2 skipped\033[1;37m, \033[0;33m1 undefined\033[1;37m, \033[1;32m1 passed\033[1;37m)\033[0m\n"
        "\n"
        "\033[0;33mYou can implement step definitions for undefined steps with these snippets:\n"
        "\n"
        "# -*- coding: utf-8 -*-\n"
        "from lettuce import step\n"
        "\n"
        "@step(u'And this one does not even has definition')\n"
        "def and_this_one_does_not_even_has_definition(step):\n"
        "    assert False, 'This step must be implemented'\033[0m"
        "\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_successful_outline_colorless():
    "With colorless output, a successful outline scenario should print beautifully."

    runner = Runner(feature_name('success_outline'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        '\n'
        'Feature: Successful Scenario Outline                          # tests/functional/output_features/success_outline/success_outline.feature:1\n'
        '  As lettuce author                                           # tests/functional/output_features/success_outline/success_outline.feature:2\n'
        '  In order to finish the first release                        # tests/functional/output_features/success_outline/success_outline.feature:3\n'
        '  I want to make scenario outlines work :)                    # tests/functional/output_features/success_outline/success_outline.feature:4\n'
        '\n'
        '  Scenario Outline: fill a web form                           # tests/functional/output_features/success_outline/success_outline.feature:6\n'
        '    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/success_outline/success_outline_steps.py:21\n'
        '    And click on "sign-up"                                    # tests/functional/output_features/success_outline/success_outline_steps.py:25\n'
        '    When I fill the field "username" with "<username>"        # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "password" with "<password>"         # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "email" with "<email>"               # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I click "done"                                        # tests/functional/output_features/success_outline/success_outline_steps.py:33\n'
        '    Then I see the title of the page is "<title>"             # tests/functional/output_features/success_outline/success_outline_steps.py:37\n'
        '\n'
        '  Examples:\n'
        '    | username | password | email          | title             |\n'
        '    | john     | doe-1234 | john@gmail.org | John \| My Website |\n'
        '    | mary     | wee-9876 | mary@email.com | Mary \| My Website |\n'
        '    | foo      | foo-bar  | foo@bar.com    | Foo \| My Website  |\n'
        '\n'
        '1 feature (1 passed)\n'
        '3 scenarios (3 passed)\n'
        '24 steps (24 passed)\n'
    )

@with_setup(prepare_stdout)
def test_output_with_successful_outline_colorful():
    "With colored output, a successful outline scenario should print beautifully."

    runner = Runner(feature_name('success_outline'), verbosity=4)
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        '\033[1;37mFeature: Successful Scenario Outline                          \033[1;30m# tests/functional/output_features/success_outline/success_outline.feature:1\033[0m\n'
        '\033[1;37m  As lettuce author                                           \033[1;30m# tests/functional/output_features/success_outline/success_outline.feature:2\033[0m\n'
        '\033[1;37m  In order to finish the first release                        \033[1;30m# tests/functional/output_features/success_outline/success_outline.feature:3\033[0m\n'
        '\033[1;37m  I want to make scenario outlines work :)                    \033[1;30m# tests/functional/output_features/success_outline/success_outline.feature:4\033[0m\n'
        '\n'
        '\033[1;37m  Scenario Outline: fill a web form                           \033[1;30m# tests/functional/output_features/success_outline/success_outline.feature:6\033[0m\n'
        '\033[0;36m    Given I open browser at "http://www.my-website.com/"      \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:21\033[0m\n'
        '\033[0;36m    And click on "sign-up"                                    \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:25\033[0m\n'
        '\033[0;36m    When I fill the field "username" with "<username>"        \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "password" with "<password>"         \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "password-confirm" with "<password>" \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "email" with "<email>"               \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I click "done"                                        \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:33\033[0m\n'
        '\033[0;36m    Then I see the title of the page is "<title>"             \033[1;30m# tests/functional/output_features/success_outline/success_outline_steps.py:37\033[0m\n'
        '\n'
        '\033[1;37m  Examples:\033[0m\n'
        '\033[0;36m   \033[1;37m |\033[0;36m username\033[1;37m |\033[0;36m password\033[1;37m |\033[0;36m email         \033[1;37m |\033[0;36m title            \033[1;37m |\033[0;36m\033[0m\n'
        '\033[1;32m   \033[1;37m |\033[1;32m john    \033[1;37m |\033[1;32m doe-1234\033[1;37m |\033[1;32m john@gmail.org\033[1;37m |\033[1;32m John \| My Website\033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m   \033[1;37m |\033[1;32m mary    \033[1;37m |\033[1;32m wee-9876\033[1;37m |\033[1;32m mary@email.com\033[1;37m |\033[1;32m Mary \| My Website\033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m   \033[1;37m |\033[1;32m foo     \033[1;37m |\033[1;32m foo-bar \033[1;37m |\033[1;32m foo@bar.com   \033[1;37m |\033[1;32m Foo \| My Website \033[1;37m |\033[1;32m\033[0m\n'
        '\n'
        "\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m3 scenarios (\033[1;32m3 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m24 steps (\033[1;32m24 passed\033[1;37m)\033[0m\n"
    )

@with_setup(prepare_stdout)
def test_output_with_failful_outline_colorless():
    "With colorless output, an unsuccessful outline scenario should print beautifully."

    runner = Runner(feature_name('fail_outline'), verbosity=3)
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        'Feature: Failful Scenario Outline                             # tests/functional/output_features/fail_outline/fail_outline.feature:1\n'
        '  As lettuce author                                           # tests/functional/output_features/fail_outline/fail_outline.feature:2\n'
        '  In order to finish the first release                        # tests/functional/output_features/fail_outline/fail_outline.feature:3\n'
        '  I want to make scenario outlines work :)                    # tests/functional/output_features/fail_outline/fail_outline.feature:4\n'
        '\n'
        '  Scenario Outline: fill a web form                           # tests/functional/output_features/fail_outline/fail_outline.feature:6\n'
        '    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/fail_outline/fail_outline_steps.py:21\n'
        '    And click on "sign-up"                                    # tests/functional/output_features/fail_outline/fail_outline_steps.py:25\n'
        '    When I fill the field "username" with "<username>"        # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "password" with "<password>"         # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "email" with "<email>"               # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I click "done"                                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:33\n'
        '    Then I see the message "<message>"                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:37\n'
        '\n'
        '  Examples:\n'
        '    | username | password | email          | message       |\n'
        '    | john     | doe-1234 | john@gmail.org | Welcome, John |\n'
        '    | mary     | wee-9876 | mary@email.com | Welcome, Mary |\n'
        "    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 30, in when_i_fill_the_field_x_with_y\n'
        "        if field == 'password' and value == 'wee-9876':  assert False\n"
        "    AssertionError\n"
        '    | foo      | foo-bar  | foo@bar.com    | Welcome, Foo  |\n'
        '\n'
        '1 feature (0 passed)\n'
        '3 scenarios (1 failed, 2 passed)\n'
        '24 steps (1 failed, 4 skipped, 19 passed)\n' % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'fail_outline', 'fail_outline_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_failful_outline_colorful():
    "With colored output, an unsuccessful outline scenario should print beautifully."

    runner = Runner(feature_name('fail_outline'), verbosity=4)
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        '\033[1;37mFeature: Failful Scenario Outline                             \033[1;30m# tests/functional/output_features/fail_outline/fail_outline.feature:1\033[0m\n'
        '\033[1;37m  As lettuce author                                           \033[1;30m# tests/functional/output_features/fail_outline/fail_outline.feature:2\033[0m\n'
        '\033[1;37m  In order to finish the first release                        \033[1;30m# tests/functional/output_features/fail_outline/fail_outline.feature:3\033[0m\n'
        '\033[1;37m  I want to make scenario outlines work :)                    \033[1;30m# tests/functional/output_features/fail_outline/fail_outline.feature:4\033[0m\n'
        '\n'
        '\033[1;37m  Scenario Outline: fill a web form                           \033[1;30m# tests/functional/output_features/fail_outline/fail_outline.feature:6\033[0m\n'
        '\033[0;36m    Given I open browser at "http://www.my-website.com/"      \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:21\033[0m\n'
        '\033[0;36m    And click on "sign-up"                                    \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:25\033[0m\n'
        '\033[0;36m    When I fill the field "username" with "<username>"        \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "password" with "<password>"         \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "password-confirm" with "<password>" \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I fill the field "email" with "<email>"               \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:29\033[0m\n'
        '\033[0;36m    And I click "done"                                        \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:33\033[0m\n'
        '\033[0;36m    Then I see the message "<message>"                        \033[1;30m# tests/functional/output_features/fail_outline/fail_outline_steps.py:37\033[0m\n'
        '\n'
        '\033[1;37m  Examples:\033[0m\n'
        '\033[0;36m   \033[1;37m |\033[0;36m username\033[1;37m |\033[0;36m password\033[1;37m |\033[0;36m email         \033[1;37m |\033[0;36m message      \033[1;37m |\033[0;36m\033[0m\n'
        '\033[1;32m   \033[1;37m |\033[1;32m john    \033[1;37m |\033[1;32m doe-1234\033[1;37m |\033[1;32m john@gmail.org\033[1;37m |\033[1;32m Welcome, John\033[1;37m |\033[1;32m\033[0m\n'
        '\033[1;32m   \033[1;37m |\033[1;32m mary    \033[1;37m |\033[1;32m wee-9876\033[1;37m |\033[1;32m mary@email.com\033[1;37m |\033[1;32m Welcome, Mary\033[1;37m |\033[1;32m\033[0m\n'
        "\033[1;31m    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 30, in when_i_fill_the_field_x_with_y\n'
        "        if field == 'password' and value == 'wee-9876':  assert False\n"
        "    AssertionError\033[0m\n"
        '\033[1;32m   \033[1;37m |\033[1;32m foo     \033[1;37m |\033[1;32m foo-bar \033[1;37m |\033[1;32m foo@bar.com   \033[1;37m |\033[1;32m Welcome, Foo \033[1;37m |\033[1;32m\033[0m\n'
        '\n'
        "\033[1;37m1 feature (\033[0;31m0 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m3 scenarios (\033[1;32m2 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m24 steps (\033[0;31m1 failed\033[1;37m, \033[0;36m4 skipped\033[1;37m, \033[1;32m19 passed\033[1;37m)\033[0m\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'fail_outline', 'fail_outline_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stderr)
def test_many_features_a_file():
    "syntax checking: Fail if a file has more than one feature"

    filename = syntax_feature_name('many_features_a_file')
    runner = Runner(filename)
    assert_raises(SystemExit, runner.run)

    assert_stderr_lines(
        'Syntax error at: %s\n'
        'A feature file must contain ONLY ONE feature!\n' % filename
    )

@with_setup(prepare_stderr)
def test_feature_without_name():
    "syntax checking: Fail on features without name"

    filename = syntax_feature_name('feature_without_name')
    runner = Runner(filename)
    assert_raises(SystemExit, runner.run)

    assert_stderr_lines(
        'Syntax error at: %s\n'
        'Features must have a name that start with a word letter (not an odd character). e.g: "Feature: This is my name"\n'
        % filename
    )

@with_setup(prepare_stderr)
def test_feature_with_invalid_name():
    "syntax checking: Fail on features with an invalid name"

    filename = syntax_feature_name('feature_with_invalid_name')
    runner = Runner(filename)
    assert_raises(SystemExit, runner.run)

    assert_stderr_lines(
        'Syntax error at: %s\n'
        'Features must have a name that start with a word letter (not an odd character). e.g: "Feature: This is my name"\n'
        % filename
    )


@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_double_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within double quotes. colorless"

    runner = Runner(feature_name('double-quoted-snippet'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: double-quoted snippet proposal                          # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:3 (undefined)\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'1 step (1 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    assert False, \'This step must be implemented\'\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_double_quotes_colorful():
    "Testing that the proposed snippet is clever enough to identify groups within double quotes. colorful"

    runner = Runner(feature_name('double-quoted-snippet'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'\033[1;37mFeature: double-quoted snippet proposal                          \033[1;30m# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:1\033[0m\n'
        u'\n'
        u'\033[1;37m  Scenario: Propose matched groups                               \033[1;30m# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:2\033[0m\n'
        u'\033[0;33m    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" \033[1;30m# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:3\033[0m\n'
        u'\n'
        "\033[1;37m1 feature (\033[0;31m0 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 scenario (\033[0;31m0 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 step (\033[0;33m1 undefined\033[1;37m, \033[1;32m0 passed\033[1;37m)\033[0m\n"
        u'\n'
        u'\033[0;33mYou can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    assert False, \'This step must be implemented\'\033[0m\n'
    )


@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_single_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within single quotes. colorless"

    runner = Runner(feature_name('single-quoted-snippet'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: single-quoted snippet proposal                          # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:2\n'
        u'    Given I have \'stuff here\' and \'more @#$%ˆ& bizar sutff h3r3\' # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:3 (undefined)\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'1 step (1 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have \\\'(.*)\\\' and \\\'(.*)\\\'\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    assert False, \'This step must be implemented\'\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_single_quotes_colorful():
    "Testing that the proposed snippet is clever enough to identify groups within single quotes. colorful"

    runner = Runner(feature_name('single-quoted-snippet'), verbosity=4)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'\033[1;37mFeature: single-quoted snippet proposal                          \033[1;30m# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:1\033[0m\n'
        u'\n'
        u'\033[1;37m  Scenario: Propose matched groups                               \033[1;30m# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:2\033[0m\n'
        u'\033[0;33m    Given I have \'stuff here\' and \'more @#$%ˆ& bizar sutff h3r3\' \033[1;30m# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:3\033[0m\n'
        u'\n'
        "\033[1;37m1 feature (\033[0;31m0 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 scenario (\033[0;31m0 passed\033[1;37m)\033[0m\n" \
        "\033[1;37m1 step (\033[0;33m1 undefined\033[1;37m, \033[1;32m0 passed\033[1;37m)\033[0m\n"
        u'\n'
        u'\033[0;33mYou can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have \\\'(.*)\\\' and \\\'(.*)\\\'\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    assert False, \'This step must be implemented\'\033[0m\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_redundant_quotes():
    "Testing that the proposed snippet is clever enough to avoid duplicating the same snippet"

    runner = Runner(feature_name('redundant-steps-quotes'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: avoid duplicating same snippet                          # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:3 (undefined)\n'
        u'    Given I have "blablabla" and "12345"                         # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:4 (undefined)\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'2 steps (2 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    assert False, \'This step must be implemented\'\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_normalized_unicode_names():
    "Testing that the proposed snippet is clever enough normalize method names even with latin accents"

    runner = Runner(feature_name('latin-accents'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u"\n"
        u"Funcionalidade: melhorar o output de snippets do lettuce                                      # tests/functional/output_features/latin-accents/latin-accents.feature:2\n"
        u"  Como autor do lettuce                                                                       # tests/functional/output_features/latin-accents/latin-accents.feature:3\n"
        u"  Eu quero ter um output refinado de snippets                                                 # tests/functional/output_features/latin-accents/latin-accents.feature:4\n"
        u"  Para melhorar, de uma forma geral, a vida do programador                                    # tests/functional/output_features/latin-accents/latin-accents.feature:5\n"
        u"\n"
        u"  Cenário: normalizar snippets com unicode                                                    # tests/functional/output_features/latin-accents/latin-accents.feature:7\n"
        u"    Dado que eu tenho palavrões e outras situações                                            # tests/functional/output_features/latin-accents/latin-accents.feature:8 (undefined)\n"
        u"    E várias palavras acentuadas são úteis, tais como: \"(é,não,léo,chororó,chácara,epígrafo)\" # tests/functional/output_features/latin-accents/latin-accents.feature:9 (undefined)\n"
        u"    Então eu fico felizão                                                                     # tests/functional/output_features/latin-accents/latin-accents.feature:10 (undefined)\n"
        u"\n"
        u"1 feature (0 passed)\n"
        u"1 scenario (0 passed)\n"
        u"3 steps (3 undefined, 0 passed)\n"
        u"\n"
        u"You can implement step definitions for undefined steps with these snippets:\n"
        u"\n"
        u"# -*- coding: utf-8 -*-\n"
        u"from lettuce import step\n"
        u"\n"
        u"@step(u'Dado que eu tenho palavrões e outras situações')\n"
        u"def dado_que_eu_tenho_palavroes_e_outras_situacoes(step):\n"
        u"    assert False, 'This step must be implemented'\n"
        u"@step(u'E várias palavras acentuadas são úteis, tais como: \"(.*)\"')\n"
        u"def e_varias_palavras_acentuadas_sao_uteis_tais_como_group1(step, group1):\n"
        u"    assert False, 'This step must be implemented'\n"
        u"@step(u'Então eu fico felizão')\n"
        u"def entao_eu_fico_felizao(step):\n"
        u"    assert False, 'This step must be implemented'\n"
    )

@with_setup(prepare_stdout)
def test_output_level_2_success():
    'Output with verbosity 2 must show only the scenario names, followed by "... OK" in case of success'

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_scenarios'), verbosity=2)
    runner.run()

    assert_stdout_lines(
        "Do nothing ... OK\n"
        "Do nothing (again) ... OK\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_level_2_fail():
    'Output with verbosity 2 must show only the scenario names, followed by "... FAILED" in case of fail'

    runner = Runner(feature_name('failed_table'), verbosity=2)
    runner.run()

    assert_stdout_lines_with_traceback(
        "See it fail ... FAILED\n"
        "\n"
        "Traceback (most recent call last):\n"
        '  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "    ret = self.function(self.step, *args, **kw)\n"
        '  File "%(step_file)s", line 25, in tof\n'
        "    assert False\n"
        "AssertionError\n"
        "\n"
        "1 feature (0 passed)\n"
        "1 scenario (0 passed)\n"
        "5 steps (1 failed, 2 skipped, 1 undefined, 1 passed)\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_level_2_error():
    'Output with verbosity 2 must show only the scenario names, followed by "... ERROR" in case of fail'

    runner = Runner(feature_name('error_traceback'), verbosity=2)
    runner.run()

    assert_stdout_lines_with_traceback(
        "It should pass ... OK\n"
        "It should raise an exception different of AssertionError ... ERROR\n"
        "\n"
        "Traceback (most recent call last):\n"
        '  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "    ret = self.function(self.step, *args, **kw)\n"
        '  File "%(step_file)s", line 10, in given_my_step_that_blows_a_exception\n'
        "    raise RuntimeError\n"
        "RuntimeError\n"
        "\n"
        "1 feature (0 passed)\n"
        "2 scenarios (1 passed)\n"
        "2 steps (1 failed, 1 passed)\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'error_traceback', 'error_traceback_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_level_1_success():
    'Output with verbosity 2 must show only the scenario names, followed by "... OK" in case of success'

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_scenarios'), verbosity=1)
    runner.run()

    assert_stdout_lines(
        ".."
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_level_1_fail():
    'Output with verbosity 2 must show only the scenario names, followed by "... FAILED" in case of fail'

    runner = Runner(feature_name('failed_table'), verbosity=1)
    runner.run()

    assert_stdout_lines_with_traceback(
        ".F...\n"
        "\n"
        "Traceback (most recent call last):\n"
        '  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "    ret = self.function(self.step, *args, **kw)\n"
        '  File "%(step_file)s", line 25, in tof\n'
        "    assert False\n"
        "AssertionError\n"
        "\n"
        "1 feature (0 passed)\n"
        "1 scenario (0 passed)\n"
        "5 steps (1 failed, 2 skipped, 1 undefined, 1 passed)\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_level_1_error():
    'Output with verbosity 2 must show only the scenario names, followed by "... ERROR" in case of fail'

    runner = Runner(feature_name('error_traceback'), verbosity=1)
    runner.run()

    assert_stdout_lines_with_traceback(
        ".E\n"
        "\n"
        "Traceback (most recent call last):\n"
        '  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "    ret = self.function(self.step, *args, **kw)\n"
        '  File "%(step_file)s", line 10, in given_my_step_that_blows_a_exception\n'
        "    raise RuntimeError\n"
        "RuntimeError\n"
        "\n"
        "1 feature (0 passed)\n"
        "2 scenarios (1 passed)\n"
        "2 steps (1 failed, 1 passed)\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'error_traceback', 'error_traceback_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_commented_scenario():
    'Test one commented scenario'

    runner = Runner(feature_name('commented_feature'), verbosity=1)
    runner.run()

    assert_stdout_lines(
        "."
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "1 step (1 passed)\n"
    )


@with_setup(prepare_stdout)
def test_blank_step_hash_value():
    "syntax checking: Blank in step hash column = empty string"

    

    @step('ignore step')
    def append_2_more(step):
        pass

    @step('string length calc')
    def append_2_more(step):
        for hash in step.hashes:
            if len(hash["string"])+len(hash["string2"]) != int(hash["length"]):
                raise AssertionError("fail")

    filename = syntax_feature_name('blank_values_in_hash')
    runner = Runner(filename, verbosity=1)
    runner.run()

    assert_stdout_lines(
        "...."
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "4 steps (4 passed)\n"
    )

class MockPrevResultPersister(object):
    def __init__(self, initial_results_list = None):
        self.initial_results_list = initial_results_list or {}
        self.final_results_list = None
    def read_previous_results(self):
        return self.initial_results_list
    def write_results(self, results):
        self.final_results_list = results 

@with_setup(prepare_stdout)
def test_syntax_check_only():
    "syntax checking: Show a list of all steps that do not have matching functions, don't actually run any steps"

    @step('matching step')
    def append_2_more(step):
        raise AssertionError('should not be run')

    filename = syntax_feature_name('syntax_check_only')
    # Verbosity of zero so only get syntax output
    persister = MockPrevResultPersister([])
    run_controller = RunController(persister, only_run_failed=False, only_syntax_check=True)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Syntax errors:\n"
        "    When I do something unrecognised      # tests/functional/syntax_features/syntax_check_only/syntax_check_only.feature:5 (undefined)\n"
        "    Then the syntax check should complain # tests/functional/syntax_features/syntax_check_only/syntax_check_only.feature:6 (undefined)\n"
    )

@with_setup(prepare_stdout)
def test_gather_failed_test_ids():
    "failed test checking: Test that gathers details on which tests (scenarios) have failed"

    @step('working step')
    def append_2_more(step):
        pass

    @step('breaking step')
    def append_2_more(step):
        raise AssertionError('bang')

    filename = failed_feature_name('some_failing_scenarios')
    # Verbosity of zero so only get syntax output
    persister = MockPrevResultPersister(None)
    # Initial run, should run all steps initially and we should end up with which steps failed
    run_controller = RunController(persister, only_run_failed=True, only_syntax_check=False)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Check we caught and stored which steps failed and which passed
    res = persister.final_results_list
    assert_equals(len(res), 5)
    assert_equals(res[1].status, ScenarioResultSummary.FAILED)
    assert_equals(res[2].status, ScenarioResultSummary.FAILED)
    assert_equals(res[3].status, ScenarioResultSummary.PASSED)
    assert_equals(res[4].status, ScenarioResultSummary.PASSED)
    assert_equals(res[5].status, ScenarioResultSummary.FAILED)

@with_setup(prepare_stdout)
def test_gather_second_pass_failed_test_ids():
    "failed test checking: Test that gathers not_run and which tests (scenarios) have failed on second run"

    @step('working step')
    def append_2_more(step):
        pass

    @step('breaking step')
    def append_2_more(step):
        raise AssertionError('bang')

    filename = failed_feature_name('some_failing_scenarios')
    # Verbosity of zero so only get syntax output
    scenarioSummaries={}
    scenarioSummaries[1] = ScenarioResultSummary(1, ScenarioResultSummary.FAILED)
    scenarioSummaries[2] = ScenarioResultSummary(2, ScenarioResultSummary.FAILED)
    scenarioSummaries[3] = ScenarioResultSummary(3, ScenarioResultSummary.PASSED)
    scenarioSummaries[4] = ScenarioResultSummary(4, ScenarioResultSummary.PASSED)
    scenarioSummaries[5] = ScenarioResultSummary(5, ScenarioResultSummary.FAILED)
    persister = MockPrevResultPersister(scenarioSummaries)
    # Initial run, should run all steps initially and we should end up with which steps failed
    run_controller = RunController(persister, only_run_failed=True, only_syntax_check=False)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Check we caught and stored which steps failed and which passed
    res = persister.final_results_list
    assert_equals(len(res), 5)
    assert_equals(res[1].status, ScenarioResultSummary.FAILED)
    assert_equals(res[2].status, ScenarioResultSummary.FAILED)
    assert_equals(res[3].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[4].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[5].status, ScenarioResultSummary.FAILED)

@with_setup(prepare_stdout)
def test_gather_third_pass_failed_test_ids():
    "failed test checking: Test that gathers not_run and which tests (scenarios) have failed on second run"

    @step('working step')
    def append_2_more(step):
        pass

    @step('breaking step')
    def append_2_more(step):
        raise AssertionError('bang')

    filename = failed_feature_name('some_failing_scenarios')
    # Verbosity of zero so only get syntax output
    scenarioSummaries={}
    scenarioSummaries[1] = ScenarioResultSummary(1, ScenarioResultSummary.FAILED)
    scenarioSummaries[2] = ScenarioResultSummary(2, ScenarioResultSummary.FAILED)
    scenarioSummaries[3] = ScenarioResultSummary(3, ScenarioResultSummary.NOT_RUN)
    scenarioSummaries[4] = ScenarioResultSummary(4, ScenarioResultSummary.NOT_RUN)
    scenarioSummaries[5] = ScenarioResultSummary(5, ScenarioResultSummary.FAILED)
    persister = MockPrevResultPersister(scenarioSummaries)
    run_controller = RunController(persister, only_run_failed=True, only_syntax_check=False)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Check we caught and stored which steps failed and which passed
    res = persister.final_results_list
    assert_equals(len(res), 5)
    assert_equals(res[1].status, ScenarioResultSummary.FAILED)
    assert_equals(res[2].status, ScenarioResultSummary.FAILED)
    assert_equals(res[3].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[4].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[5].status, ScenarioResultSummary.FAILED)

@with_setup(prepare_stdout)
def test_scenario_outlines_with_failed_only():
    "failed test checking: Test that works with scenario outlines if only some outlines fail"

    @step('I have entered')
    def append_2_more(step):
        pass
    
    @step('result should be')
    def append_2_more(step):
        pass

    @step('When I press add')
    def append_2_more(step):
        pass

    filename = failed_feature_name('failing_scenario_outlines')
    # Verbosity of zero so only get syntax output
    persister = MockPrevResultPersister(None)
    # Initial run, should run all steps initially and we should end up with which steps failed
    run_controller = RunController(persister, only_run_failed=True, only_syntax_check=False)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Check we caught and stored which steps failed and which passed
    res = persister.final_results_list
    assert_equals(len(res), 4)
    assert_equals(res[1].status, ScenarioResultSummary.PASSED)
    assert_equals(res[2].status, ScenarioResultSummary.FAILED)
    assert_equals(res[3].status, ScenarioResultSummary.PASSED)
    assert_equals(res[4].status, ScenarioResultSummary.FAILED)

@with_setup(prepare_stdout)
def test_scenario_outlines_with_failed_only_second_run():
    "failed test checking: Test that works with scenario outlines if only some outlines fail - second run"

    @step('I have entered')
    def append_2_more(step):
        pass
    
    @step('result should be')
    def append_2_more(step):
        pass

    @step('When I press add')
    def append_2_more(step):
        pass

    filename = failed_feature_name('failing_scenario_outlines')
    # Verbosity of zero so only get syntax output
    scenarioSummaries={}
    scenarioSummaries[1] = ScenarioResultSummary(1, ScenarioResultSummary.PASSED)
    scenarioSummaries[2] = ScenarioResultSummary(2, ScenarioResultSummary.FAILED)
    scenarioSummaries[3] = ScenarioResultSummary(3, ScenarioResultSummary.PASSED)
    scenarioSummaries[4] = ScenarioResultSummary(4, ScenarioResultSummary.FAILED)
    persister = MockPrevResultPersister(scenarioSummaries)
    run_controller = RunController(persister, only_run_failed=True, only_syntax_check=False)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Check we caught and stored which steps failed and which passed
    res = persister.final_results_list
    assert_equals(len(res), 4)
    assert_equals(res[1].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[2].status, ScenarioResultSummary.FAILED)
    assert_equals(res[3].status, ScenarioResultSummary.NOT_RUN)
    assert_equals(res[4].status, ScenarioResultSummary.FAILED)

def test_run_only_scenarios_tagged():
    "Test that only scenarios that have the right tags on them get run"

    world.colours = []
    
    @step('Running "(.*)" scenario')
    def keep_colours(step, colour):
        world.colours.append(colour)

    filename = tag_feature_name('all_colours')
    persister = MockPrevResultPersister()
    
    # Check all are run if no tags given
    run_controller = RunController(persister)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Make sure tags don't corrupt the name of the scenarios or the feature
    assert_equals("Test tags with multiple tagged steps", runner.feature_for_test.name)
    assert_equals("red scenario", runner.feature_for_test.scenarios[0].name)
    assert_equals("blue scenario", runner.feature_for_test.scenarios[1].name)
    # Check the actual tags associated with everything are what we expect
    assert_equals(["primary", "purple", "orange"], runner.feature_for_test.tags)
    assert_equals(["red", "primary", "purple", "orange"], runner.feature_for_test.scenarios[0].tags)
    assert_equals(["blue", "primary", "purple", "orange"], runner.feature_for_test.scenarios[1].tags)
    assert_equals(["red", "blue", "primary", "purple", "orange"], runner.feature_for_test.scenarios[2].tags)
    # Check what actually got run
    assert_equals(["red", "blue", "purple", "black"], world.colours)
    
    # Only run red - so runs red and purple (red+blue)
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["@red"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["red", "purple"], world.colours)
    
    # Run all except red (which includes purple)
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["~@red"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["blue", "black"], world.colours)
    
    # Run red AND blue - so runs purple
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["@red,@blue"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["purple"], world.colours)
    
    # Run red AND blue OR black - so runs purple and black
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["@red,@blue", "@black"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["purple", "black"], world.colours)
    
    # Run red AND NOT blue - so runs red only
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["@red,~@blue"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["red"], world.colours)
    
    # Only run primary (which should include everything)
    world.colours = []
    run_controller = RunController(persister, tags_to_run=["@primary"])
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    assert_equals(["red", "blue", "purple", "black"], world.colours)

def test_nasty_tags_in_descriptions():
    "Test that can parse correctly when people are putting tags into descriptions etc"

    world.colours = []
    
    @step('Running "(.*)" scenario')
    def keep_colours(step, colour):
        world.colours.append(colour)

    filename = tag_feature_name('nasty_tag_filled')
    persister = MockPrevResultPersister()
    
    # Check all are run if no tags given
    run_controller = RunController(persister)
    runner = Runner(filename, verbosity=0, run_controller = run_controller)
    runner.run()
    # Make sure tags don't corrupt the name of the scenarios or the feature
    assert_equals("Test with multiple @tagged steps", runner.feature_for_test.name)
    # Only first line counts as name of scenario
    assert_equals("red scenario with tags in the scenario @name",
                  runner.feature_for_test.scenarios[0].name)
    assert_equals("blue scenario", runner.feature_for_test.scenarios[1].name)
    # Check the actual tags associated with everything are what we expect
    assert_equals(["primary", "purple", "orange"], runner.feature_for_test.tags)
    assert_equals(["red", "primary", "purple", "orange"], runner.feature_for_test.scenarios[0].tags)
    assert_equals(["blue", "primary", "purple", "orange"], runner.feature_for_test.scenarios[1].tags)
    assert_equals(["red", "blue", "primary", "purple", "orange"], runner.feature_for_test.scenarios[2].tags)
    # Check what actually got run, nothing bad happened we hope from our parsing of the tags and lines
    assert_equals(["red", "blue", "purple", "black"], world.colours)
    
