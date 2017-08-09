"""
Write a blog in plain text with multiple entries per file

This module includes tools for working with parrot38 blog files
"""
__version__ = "0.0.1"
__author__ = "Vitaly Potyarkin"


import re
from collections import deque, namedtuple, UserDict
from itertools import chain


DEFAULT_DELIMITER = ":"
META_PATTERN = r"^::(\w+)::(.*)$"
META_ESCAPED = META_PATTERN.replace("^", r"^\\", 1)


class Delimiter(namedtuple("DelimiterTuple", "char default pattern esc_pattern")):
    """
    Delimiter(char) -> new delimiter for parrot38

    By default a colon symbol is used (char=":")

    Delimiter has following attributes:

    char
        A single character used to build the delimiter
    default
        Default delimiter line
    pattern
        Regex pattern for matching delimiters
    esc_pattern
        Regex pattern for matching escaped delimiters
    """
    __slots__ = ()

    def __new__(cls, char=DEFAULT_DELIMITER):
        """Make new Delimiter from char. Override namedtuple constructor"""
        if len(char) != 1:
            raise ValueError("delimiter has to be a single character")
        pattern = r"^\%s{7,}$" % char
        esc_pattern = pattern.replace("^", r"^\\", 1)
        self = super(Delimiter, cls).__new__(cls,
                                             char,
                                             char * 38,
                                             pattern,
                                             esc_pattern)
        return self

    def _make(*a, **kw):
        raise AttributeError("object has no attribute '_make'")


class WriteOnceDict(UserDict):
    """A dictionary that does not allow overwriting previously saved values"""
    def __setitem__(self, key, value):
        """Block overwriting values"""
        if key in self:
            raise AttributeError(
                      "{cls} already has value for '{key}': '{value}'".format(
                          cls=type(self).__name__,
                          key=key,
                          value=self[key],
                      )
                  )
        else:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        """Block deleting items"""
        raise AttributeError("Deleting items from %s is not allowed"
                             % type(self).__name__)


class BlogPost(object):
    pass


def parse(lines, backwards=False, delimiter=DEFAULT_DELIMITER):
    """
    Parse parrot38 input into a sequence of dictionaries. Each dictionary
    corresponds to a blog post.

    Arguments:
    lines
        Sequence of lines with line break at the end, preferably a generator.
        This can be, for example, the result of TextIOWrapper.readlines()
        method.
    backwards
        Shows whether lines were read in inverted order,
        bottom to top. Default: False.
    delimiter
        Single character used to build parrot38 entry delimiter.

    Yields dictionaries where "body" key points to post body, and other keys
    are metadata keys with corresponding values.
    """
    delim = Delimiter(delimiter)
    RegexCollection = namedtuple("RegexCollection",
                                 "delim meta esc_delim esc_meta")
    regex = RegexCollection._make(
                re.compile(pattern) for pattern in [
                    delim.pattern,
                    META_PATTERN,
                    delim.esc_pattern,
                    META_ESCAPED,
                ]
            )

    line_number = 0
    entry, body, empty = WriteOnceDict(), deque(), True  # begin new post
    for line in chain(lines, [delim.default]):
        line_number += 1  # count lines for traceback
        original_line = line
        try:
            match = None
            for pattern in regex:
                match = pattern.match(line)
                if match: break
            if match:
                if pattern in {regex.esc_delim, regex.esc_meta}:
                    line = line[1:]  # drop first backslash from escaped line
                else:
                    line = None  # drop markup line from entry
                    if pattern == regex.meta:
                        meta_key, meta_value = match.groups()
                        entry[meta_key.lower()] = meta_value.strip()
                    elif pattern == regex.delim:
                        if not empty:
                            if backwards: body.reverse()
                            entry["body"] = "".join(body).strip()
                            yield entry
                        entry, body, empty = WriteOnceDict(), deque(), True
                    else:
                        raise RuntimeError("matched unknown pattern: %s"
                                           % pattern)
            if line is not None:
                body.append(line)
                if empty: empty = not(bool(line.strip()))
        except Exception as e:
            message = "error while parsing line {num}: {line}".format(
                          num=line_number,
                          line=original_line)
            raise ValueError(message) from e


def load(filenames, *a, **kw):
    """
    Generator that reads parrot38 blog posts from multiple plain text files

    Arguments:
    filenames
        A path or sequence of paths to files with parrot38 blog entries
    *a, **kw
        All extra arguments will be passed to Python built-in open() function
        for reading these files. Intended use case: specifying text encoding,
        line break style, etc.
    """
    if isinstance(filenames, str): filenames = [filenames]
    for filename in filenames:
        lines = read_lines(filename, *a, **kw)
        for post in parse(lines):
            yield post


def read_lines(filename, *open_args, **open_kwargs):
    """
    Generator function that reads a text file line by line.
    Extra arguments are passed to open() function.
    """
    with open(filename, *open_args, **open_kwargs) as file:
        for line in file:
            yield line


def dump(posts, filename):
    pass


def read_files(directory):
    pass
