"""
Write a blog in plain text with multiple entries per file

This module includes tools for working with parrot38 blog files
"""
__version__ = "0.0.1"
__author__ = "Vitaly Potyarkin"


import re
from collections import deque, namedtuple, UserDict
from datetime import datetime
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

    def __new__(cls, char=None):
        """Make new Delimiter from char. Override namedtuple constructor"""
        if char is None: char = DEFAULT_DELIMITER
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


def parse(lines, backwards=False, delim_char=None):
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
    delim_char
        Single character used to build parrot38 entry delimiter.

    Yields dictionaries where "body" key points to post body, and other keys
    are metadata keys with corresponding values.
    """
    if delim_char is None: delim_char = DEFAULT_DELIMITER
    delim = Delimiter(delim_char)
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
        try:
            for post in parse(lines):
                yield post
        except Exception as e:
            error_msg = "error while parsing file: {}".format(filename)
            raise ValueError(error_msg) from e


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


#
# IMPORTANT
#
# Code below makes more assumptions about input than it is required
# by parrot38 specification.
#
# Consider this an example, not a reference.
#

class BlogPost(object):
    """
    Handle a single blog entry with all metadata

    This class imposes extra restrictions on input data in addition to parrot38
    specification.

    METADATA LINES:
    date
        Required. A timestamp in one of supported human readable formats that
        will be used for sorting posts chronologically.
    modified
        Optional. A timestamp showing last modification of blog post. In `stat`
        terms this could be though of as "mtime", and date as "ctime".
    tags
        Optional. Space separated sequence of tags (categories). All non-word
        characters will be stripped when parsing.
    hidden
        Optional. If set, the post will not be rendered or published.
    """
    URL_SPACE = "-"  # single char used as word separator in URL
    DATE_FORMATS = [  # first format is considered default for output
        "%Y-%m-%d %H:%M %z",
        "%Y-%m-%d %H:%M %Z",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M:%S %Z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %z",
        "%Y-%m-%d %Z",
        "%Y-%m-%d",
        # TODO: add more formats, review sort order
        ]

    # Regular expressions are compiled once for class, because BlogPost is
    # meant to be instanciated multiple times when performing typical tasks.
    _re_header = re.compile(r"^\s*\#*\s*(.*?)\s*$")
    _re_not_urlsafe = re.compile(r"[^\w-]+")
    _re_whitespace = re.compile(r"\s+")
    _re_nonword = re.compile(r"[^\w\s]")

    def __init__(self, body, date, modified=None, tags=None, hidden=None):
        """
        Create new BlogPost instance

        Results of parse() function can be passed as **kwargs
        """
        header, text, *__ = body.split("\n", 1) + [""]
        self._title = self._re_header.sub(r"\1", header)
        self._body = text.strip()
        self._ctime = self.parse_date(date)
        if modified is not None:
            self._mtime = self.parse_date(modified)
        else:
            self._mtime = None
        if tags is not None:
            self._tags = self._re_nonword.sub("", tags).split()
        else:
            self._tags = []
        self._hidden = hidden is not None

    @property
    def title(self):
        """
        parrot38 does not require a title to be specifically set, so the first
        line of post body will be treated as one.

        Markdown heading will be stripped of leading #-characters.
        """
        return self._title

    @property
    def urltitle(self):
        """Url safe version of self.title"""
        pattern = self._re_not_urlsafe
        return pattern.sub(self.URL_SPACE, self.title).strip(self.URL_SPACE)

    @property
    def body(self):
        """Post body without first line which is treated as heading"""
        return self._body

    @property
    def ctime(self):
        """Post creation time as datetime object"""
        return self._ctime

    @property
    def mtime(self):
        """Post modification time as datetime object"""
        if self._mtime:
            mtime = self._mtime
        else:
            mtime = self._ctime
        return mtime

    @property
    def created(self):
        """Post creation time as human readable string"""
        return self.ctime.strftime(self.DATE_FORMATS[0])

    @property
    def modified(self):
        """
        Post modification time as human readable string

        If post was not modified after creation (self._mtime is None),
        this property returns empty string
        """
        if self._mtime is not None:
            mod_time = self.mtime.strftime(self.DATE_FORMATS[0])
        else:
            mod_time = ""
        return mod_time

    @property
    def tags(self):
        """List of post's tags (categories)"""
        return self._tags

    @property
    def hidden(self):
        """Shows if post is not meant for rendering and/or publishing"""
        return self._hidden

    @classmethod
    def parse_date(cls, readable_date):
        """
        Create datetime object from human readable date

        For simplicity no format guessing is implemented here, this method
        iterates through supported formats and returns the first match
        """
        spaces = cls._re_whitespace
        clean_date = spaces.sub(" ", readable_date).strip()
        for format in cls.DATE_FORMATS:
            try:
                date = datetime.strptime(clean_date, format)
            except ValueError:
                continue
            return date
        else:
            raise ValueError("date in unknown format: %s" % readable_date)

    def to_jekyll(self):
        """Convert BlogPost to a valid Jekyll post. Returns string"""
        YAML_FRONT_MATTER = ["---\n", "---\n"]
        JEKYLL_DATE_FORMAT = "%Y-%m-%d %H:%M %z"
        EMPHASIS = ["*", "*"]  # used to wrap "Last updated" line

        metadata = dict()
        metadata["title"] = self.title
        metadata["date"] = self.ctime.strftime(JEKYLL_DATE_FORMAT)
        if self.hidden: metadata["published"] = "false"
        if self.tags: metadata["tags"] = " ".join(self.tags)

        if self.mtime != self.ctime:
            last_updated = "Last updated on {}".format(
                                self.mtime.strftime(JEKYLL_DATE_FORMAT)
                            ).join(EMPHASIS) + "\n\n"
        else:
            last_updated = ""

        header = "".join("%s: %s\n" % (k, v) for k, v in metadata.items())
        return header.join(YAML_FRONT_MATTER) + last_updated + self.body
