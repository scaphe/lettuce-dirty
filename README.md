# lettuce
> Version 0.1.27 - barium

## On release names

Lettuce release names will be inspired by any green stuff.

Barium: In form of "barium nitrate" is commonly used to make green fireworks. Such a good name for a first version :)

# What

Lettuce is a [BDD](http://en.wikipedia.org/wiki/Behavior_Driven_Development) tool for python, 100% inspired on [cucumber](http://cukes.info/ "BDD with elegance and joy").

# Motivation

1. [Cucumber](http://cukes.info/) makes [Ruby](http://www.ruby-lang.org/) even more sexy. Python needed something like it.
2. Testing must be funny and easy.
3. Most python developers code in python, not ruby.
4. Ruby has Capistrano, Python has Fabric. Ruby has cucumber, Python has lettuce.
5. I personally don't like mixing many languages in small projects. Keeping all in python is better.
6. I love python, and ever did. But I also ever missed something that make writing tests easier and funnier.
7. I like [nose](http://code.google.com/p/python-nose/), which is a unittest pythonic framework. However, as the project I work on grows, so do the tests, and it becomes harder to understand them.
8. [lettuce ladies](http://www.lettuceladies.com/) :)

# Dependencies

**you will need to install these dependencies in order to** *hack* **lettuce** :)
all them are used within lettuce tests

## you could use a virtualenv:

    > mkvirtualenv lettuce
    > workon lettuce
    > pip install -r requirements.txt

## or just install manually:

    > sudo pip install -r requirements.txt

## or do it really from scratch:

* [nose](http://code.google.com/p/python-nose/)
    > [sudo] pip install nose
* [mox](http://code.google.com/p/pymox/)
    > [sudo] pip install mox
* [sphinx](http://sphinx.pocoo.org/)
    > [sudo] pip install sphinx
* [lxml](http://codespeak.net/lxml/)
    > [sudo] pip install lxml
* [django](http://djangoproject.com/)
    > [sudo] pip install django

# Contributing

1. fork and clone the project
2. install the dependencies above
3. run the tests with make:
    > make unit functional integration doctest
4. hack at will
5. commit, push etc
6. send a pull request

## keep in mind

that lettuce is a testing software, patches and pull requests must
come with automated tests, and if suitable, with proper documentation.

# mailing list

## for users

[http://groups.google.com/group/lettuce-users](http://groups.google.com/group/lettuce-users)

## for developers

[http://groups.google.com/group/lettuce-developers](http://groups.google.com/group/lettuce-developers)

# Special thanks

1. [Cucumber](http://cukes.info/) crew, for creating such a AWESOME project, and for inspiring [Lettuce](http://lettuce.it/).
2. [Tatiana](http://github.com/tatiana) for helping a lot with documentation.
3. [Django](http://djangoproject.com) which documentation structure was borrowed.
4. [Andres Jaan Tack](http://github.com/ajtack) for his awesome contributions
4. [Erlis Vidal](http://github.com/erlis) for creating a tutorial of how to install lettuce on windows.

# Known issues

## windows support

[erlis](https://github.com/erlis) have made a awesome job by making
lettuce work on windows. He posted
[here](http://www.erlisvidal.com/blog/2010/10/how-install-lettuce-windows)
how to install lettuce on windows.


# License

    <Lettuce - Behaviour Driven Development for python>
    Copyright (C) <2010-2011>  Gabriel Falcão <gabriel@nacaolivre.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
