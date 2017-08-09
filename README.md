# parrot38
Write a blog in plain text with multiple entries per file

Most static site generators (e.g. Jekyll) require each blog post to be
written it a separate text file. This is convenient for machine reading
but not very comfortable for human readers. Normal user experience with
web based blogs involves some kind of feed where user scrolls through
multiple blog entries and reads the ones of interest to him.

parrot38 offers a minimalistic way of writing a blog that is readable in
plain text form and remains renderable in the markup language used
for individual posts (Markdown, reStructuredText, HTML, etc). No markup
language for blog post body is required or assumed. parrot38 tries to be
of minimum interference with text markup languages in use today.


# Contents
There are two important parts of this project:
- parrot38 [markup specification](SPECIFICATION.md)
- [Python module](parrot38.py) that implements parsing parrot38 data and
  converting it to a form readable by popular tools (e.g. Jekyll)


## Markup example
The following example shows two blog posts written in Markdown and saved
to the same file using parrot38 markup:
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


# Contributing
All contributions are welcome!
Please check [CONTRIBUTING.md](CONTRIBUTING.md) for details


# License and copyright
Copyright © 2017 Vitaly Potyarkin
```
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use these files except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
