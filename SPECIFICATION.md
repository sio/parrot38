# parrot38 - MARKUP FOR MULTIPLE BLOG POSTS IN ONE TEXT FILE

Most static site generators (e.g. Jekyll) require each blog post to be
written it a separate text file. This is convenient for machine reading
but not very comfortable for human readers. Normal user experience with
web based blogs involves some kind of feed where user scrolls through
multiple blog entires and reads the ones of interest to him.

parrot38 offers a minimalistic way of writing a blog that is readable in
plain text form and remains renderable in the markup language used
for individual posts (Markdown, reStructuredText, HTML, etc). No markup
language for blog post body is required or assumed. parrot38 tries to be
of minimum interference with text markup languages in use today.

No sort order for posts within a file is assumed. Blog can be written with
newest entries at the top of the file or at the bottom or anywhere the
author chooses. To add timestamps use metadata lines.

parrot38 has two types of format statements:
- separators between blog entries
- metadata lines (key-value pairs)


## BLOG POST SEPARATOR

To distinguish one blog entry from another user is required to put a line
of separator characters (by default colons) between different posts.

Separator is a line made of 7 or more separator characters. By default,
it is 38 colon symbols (::::::::::::::::::::::::::::::::::::::), because
parrot38. No other characters are allowed on the separator line.

Separator means just that - a separator. One should not assume it to be
the beginning or the end of the post. Separator lines are not required at
the beginning or at the end of file.


## BLOG POST METADATA

To add metadata to the blog entry include a metadata line anywhere in the
entry. No default location is assumed.

Metadata line is a single line formatted as follows:
- Two colon symbols (::)
- Keyword - any number of word-building characters (letters and digits
  as in \w+ regex).
  Keywords are case-insensitive, "tags" and "Tags" are treated as identical.
  Each keyword can appear zero or one times within a blog post.
  Repeating keyword makes metadata invalid, no preference to first or last
  instance should be assumed.
  No spaces or punctuation marks can appear in the area enclosed by double
  colons, or the whole line will not be treated as parrot38 markup.
- Two colon symbols (::)
- Value: all text after the colon until the line break.

Keys and their value meanings/formats are not subject to this specification.
Key names and handling their values is delegated to parser implementations.


## ESCAPING parrot38 STATEMENTS WITHIN THE BLOG POST

Post separators and metadata lines are excluded from blog entry during
rendering. To put a line of the same format in the blog escape first symbol
with backslash (\\::NotMetadata:: value). Such lines will not be considered
parrot38 markup and will be rendered within the blog post without the leading
backslash.


## EXAMPLE

```markdown
::Date:: 2017-08-07
::Tags:: test parrot38

# Second blog entry - another markdown heading
Second entry is here - another markdown text

::::::::::::::::::::::::::::::::::::::
::Date:: 2017-08-06

# First blog entry - markdown heading
First entry is here - markdown text
```

This file will be rendered as two distinct blog posts, with parrot38 markup
statments stripped. Date and Tags metadata handling depends on the parser
implementation.
