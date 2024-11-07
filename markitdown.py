from __future__ import annotations

import os.path
from fileinput import filename
from typing import TypeVar, Iterable

import markdown
from bs4 import BeautifulSoup

TUnorderedList = TypeVar("TUnorderedList", bound="UnorderedList")
TOrderedList = TypeVar("TOrderedList", bound="OrderedList")
TMDlist = TypeVar("TMDlist", bound="MDlist")


class FormatingException(Exception):
    def __init__(self, message):
        super().__init__(message)


class DocText:
    parent_feature = None
    render_spaces=None

    def __init__(self, parent_feature=None):
        self.md_objects = []
        self.parent_feature = parent_feature
        self.dont_add_more_weights = False

    def _clear_weights(self):
        for i, obj in enumerate(reversed(self.md_objects)):
            new_obj = self._clear_weight(obj)
            self.md_objects[len(self.md_objects) - i - 1] = new_obj


    def _clear_weight(self, obj):
            top_obj = obj._find_top_parent()
            top_obj.child = None
            return top_obj.to_text()

    def _clear_inline_weight(self):
        top = self._clear_weight(self.md_objects[-1])
        self.md_objects[-1] = top
        self.dont_add_more_weights = True

    def _add_weight(self, func: str, text=None):
        call_function = func
        if text is None:
            if len(self.md_objects) > 0:
                if call_function == 'inlinecode':
                    self._clear_inline_weight()
                    getattr(self.md_objects[-1], call_function)()
                else:
                    if not self.dont_add_more_weights:
                        getattr(self.md_objects[-1], call_function)()
            else:
                raise FormatingException("cannot add weight no previous text exists")
        else:
            new_obj = StringFormater(text).init_class_by_name(func, text)
            self.md_objects.append(new_obj)
        return self

    def text(self, text=None):
        return self._add_weight('text', text)

    def bold(self, text=None):
        return self._add_weight('bold', text)

    def italic(self, text=None):
        return self._add_weight('italic', text)

    def inlinecode(self, text=None):
        return self._add_weight('inlinecode', text)

    def strikethrough(self, text=None):
        return self._add_weight('strikethrough', text)

    def important(self, text=None):
        return self._add_weight('important', text)

    def nospace(self, text: str = None):
        if text is None:
            self.md_objects.append(NoSpace(text))
            return self
        else:
            return self._add_weight('nospace', text)
        #
        # return self

    @staticmethod
    def _add_line_break(text, breakindex=10):
        splited = text.split(' ')
        if len(splited) > breakindex:
            for i, k in enumerate(splited):
                if i > 0:
                    if i % breakindex == 0:
                        splited[i] = '\n' + splited[i]

        return ' '.join(splited)

    def _render(self):
        md_str = ''
        nospace = False
        for i, formater in enumerate(self.md_objects):
            if not isinstance(formater, NoSpace) and not nospace:
                md_text = formater._render()
                md_str = md_str + ' ' + md_text
            elif not isinstance(formater, NoSpace) and nospace:
                md_text = formater._render()
                md_str = md_str + md_text
                nospace = False
            elif isinstance(formater, NoSpace) and formater.text_str is not None:
                md_text = formater._render()
                md_str = md_str + md_text
                # nospace=True
            else:
                nospace = True
        if self.parent_feature == Table and self.render_spaces is not None:
                spaces=''
                emptylist = [' ' for r in range(0,self.render_spaces)]
                orig_word = md_str
                spaces = spaces.join(emptylist)
                new_word = f'{orig_word}{spaces}'
                new_break_index = len(new_word)
        else:
            new_break_index = 10
            new_word = md_str

        if self.parent_feature != FencedCodeBlock:
            new_md_string = self._add_line_break(new_word,breakindex=new_break_index)
        else:
            new_md_string = new_word
        return new_md_string


class Document:

    def __init__(self, file_name=None,file_path=None):
        self.md_objects = []
        self.file_name = file_name
        self.file_path = file_path

    def quote(self, doctext: DocText|str):
        quote = Quote(doctext)
        self.md_objects.append(quote)
        return self

    def checkbox(self, doctext: DocText | str, checked=False):
        chkbox = TextCheckbox(doctext, checked)
        self.md_objects.append(chkbox)
        return self

    def heading(self, text: str, size: int = 1):
        heading = Heading(text, size)
        self.md_objects.append(heading)
        return self

    def unordered_list(self):
        unordered_list = UnorderedList()
        unordered_list.parent_document = self
        self.md_objects.append(unordered_list)
        return unordered_list

    def ordered_list(self):
        ordered_list = OrderedList()
        ordered_list.parent_document = self
        self.md_objects.append(ordered_list)
        return ordered_list

    def table(self, headers):
        table = Table(headers)
        table.parent_document = self
        self.md_objects.append(table)
        return table

    def horizontal_rule(self):
        hr = HorizaontalRule()
        self.md_objects.append(hr)
        return self

    def fenced_code_block(self, text: str | DocText):
        code_block = FencedCodeBlock(text)
        self.md_objects.append(code_block)
        return self

    def linebreak(self,amount=1):
        for _ in range(0,amount):
            self.md_objects.append(Break())
        return self

    def text(self, text_str=None):
        return self._call_by_text('text', text_str)

    def bold(self, text_str=None):
        return self._call_by_text('bold', text_str)

    def italic(self, text_str=None):
        return self._call_by_text(F'italic', text_str)

    def inlinecode(self, text_str=None):
        return self._call_by_text('inlinecode', text_str)

    def strikethrough(self, text_str=None):
        return self._call_by_text('strikethrough', text_str)

    def nospace(self, text_str=None):
        last_obj = self.md_objects[-1]
        if isinstance(last_obj, DocText):
            last_obj.nospace(text_str)
            return self
        else:
            return self._call_by_text('nospace', text_str)

    def important(self,text_str=None):
        return self._call_by_text('important', text_str)

    def render_document_text(self):
        document = ''
        for i, md in enumerate(self.md_objects):
            if i > 0:
                if isinstance(self.md_objects[i - 1], Quote) or isinstance(self.md_objects[-1], MDlist):
                    document = document + '\n\n'
                if isinstance(self.md_objects[i - 1], TextCheckbox) and isinstance(md, DocText):
                    md.md_objects.insert(0, NoSpace())  # No beginning space if previous obj is TextCheckbox
                    document = document + '\n\n'
                if isinstance(self.md_objects[i - 1], MDlist):
                    document = document + '\n'
            document = document + md._render()
        return document

    def store_document(self,html=False):
        content = self.render_document_text()
        if html:

            html_content = markdown.markdown(content,extensions=['tables'])
            new_document = BeautifulSoup()
            html_tag = new_document.new_tag('html')
            head_tag = new_document.new_tag('head')
            link_tag= new_document.new_tag('link')
            link_tag.attrs['rel'] = "stylesheet"
            link_tag.attrs['href'] = 'styles.css'
            head_tag.insert(0,link_tag)
            body_tag = new_document.new_tag('body')
            html_tag.insert(0,head_tag)
            new_document.insert(0,html_tag)
            html_tag.insert(1,body_tag)

            bf = BeautifulSoup(html_content,features="html.parser")
            body_tag.insert(0,bf)

            content = new_document.prettify(formatter="html5")
        if self.file_path is not None:
            file_and_path = os.path.join(self.file_path,self.file_name)
        else:
            file_and_path = self.file_name
        with open(file_and_path, 'w') as file:
            file.write(content)

    def _call_by_text(self, func: str, text_obj: str | DocText = None):
        """
        :param func: Name of the function to call for example 'text'
        :param text_obj: The text
        :return:
        """

        if len(self.md_objects) > 0:
            last_obj = self.md_objects[-1]
            if (not isinstance(last_obj, DocText) or isinstance(last_obj, TextCheckbox)) and isinstance(text_obj, str):
                self.md_objects.append(DocText().nospace()._add_weight(func, text=text_obj))
            elif isinstance(last_obj, TextCheckbox) and isinstance(last_obj.text_str, DocText):
                getattr(last_obj.text_str, func)()
            if isinstance(last_obj, DocText):
                getattr(last_obj, func)(text_obj)
        else:
            if isinstance(text_obj, str):
                self.md_objects.append(DocText()._add_weight(func, text=text_obj))

        return self

class Formater:

    def __init__(self):
        self.parent = None
        self.child = None
        self.parent_document = None

    @staticmethod
    def _text_escape(text: str):

        escapeable_chars = ['*', '_', '|', '`']
        escape_code = ['&#42;', '&#95;', '&#124;', '&#96;']
        for i, char in enumerate(escapeable_chars):
            text = text.replace(char, escape_code[i])
        return text

    def _find_last_child(self, obj=None):
        if obj is None:
            obj = self
        if obj.child is None:
            return obj
        else:
            return self._find_last_child(obj.child)

    def _find_top_parent(self, obj=None):
        if obj is None:
            obj = self
        if obj.parent is None or type(obj.parent) is StringFormater:
            return obj
        else:
            return self._find_top_parent(obj.parent)

    def get_parent(self) -> TOrderedList | TUnorderedList | Document:
        if self.parent is not None:
            return self.parent
        else:
            return self.parent_document

    def get_child(self)->TOrderedList | TUnorderedList:
        if self.child is not None:
            return self.child
        else:
            raise FormatingException("There is no child-list")

class FeatureFormater(Formater):

    def __init__(self, doctext: DocText | str):
        super().__init__()
        if isinstance(doctext, str):
            self.text = DocText().text(doctext)
        else:
            self.text = doctext
        self.text.parent_feature = self.__class__
        self.text._clear_weights()


class Quote(FeatureFormater):
    def __init__(self, doctext: DocText | str):
        super().__init__(doctext)

    def _render(self):
        return '\n\n> ' + self.text._render()


class FencedCodeBlock(FeatureFormater):

    def __init__(self, doctext: DocText | str):
        super().__init__(doctext)

    def _render(self):
        self.text.md_objects.insert(0, NoSpace())
        return '\n\n```\n' + self.text._render() + '\n```\n'


class TextCheckbox(Formater):

    def __init__(self, doctext: DocText | str, checked=False):
        super().__init__()
        self.text_str = None
        self.checked = checked
        if isinstance(doctext, DocText):
            self.text_str = doctext
        else:
            self.text_str = DocText().text(doctext)

    def _render(self):
        prefix = ' \n - [x] ' if self.checked else ' \n - [ ] '
        return prefix + self.text_str._render()


class MDlist(Formater):

    def __init__(self):
        super().__init__()
        self.items = []
        self.invocation_level = 0
        self.items_counter = 0
        self.block_addition = False

    def add_item(self, text: DocText | str) -> TMDlist:
        if not self.block_addition:
            if isinstance(text, str):
                self.items.append(DocText().text(text))
            elif isinstance(text, DocText):
                self.items.append(text)
            return self
        else:
            raise FormatingException(
                "Cannot do this since other non-list functions has been invoked after last item addition")

    def unordered_list(self) -> TUnorderedList:

        new_list = UnorderedList()
        new_list.parent = self
        self.child=new_list
        new_list.parent_document = self.parent_document
        new_list.invocation_level = self.invocation_level + 1
        self.items.append(new_list)
        return new_list

    def ordered_list(self) -> TOrderedList:
        new_list = OrderedList()
        new_list.parent = self
        self.child = new_list
        new_list.parent_document = self.parent_document
        new_list.invocation_level = self.invocation_level + 1
        self.items.append(new_list)
        return new_list

    def _render(self) -> str:
        doc_text = ''

        for i, item in enumerate(self.items):
            if isinstance(self, OrderedList) and not isinstance(item, MDlist):
                self.items_counter += 1
                doc_text = doc_text + ''.join(
                    ['\t' for _ in range(0, self.invocation_level)]) + f'{self.items_counter}.{item._render()}\n'
            elif isinstance(self, UnorderedList) and not isinstance(item, MDlist):
                self.items_counter += 1
                doc_text = doc_text + ''.join(['\t' for _ in range(0, self.invocation_level)]) + f'-{item._render()}\n'
            else:
                doc_text = doc_text + item._render()
        if self.parent is not None:
            return doc_text
        else:
            return '\n\n' + doc_text

    def __getattr__(self, item, *args, **kwargs):
        if hasattr(self.parent_document, item):
            self.block_addition = True

            def wrapper(*arguments, **kw) -> Document:
                return getattr(self.parent_document, item)(*arguments, **kw)

            return wrapper


class OrderedList(MDlist):

    def __init__(self):
        super().__init__()


class UnorderedList(MDlist):
    def __init__(self):
        super().__init__()


class StringFormater(Formater):
    def __init__(self, text_str: str):
        super().__init__()
        self.text_str = text_str

    def _validate(self, obj, func, funclist):

        funclist.append(obj.__class__.__name__)

        if self.get_class_by_func_name(func) in funclist:
            raise FormatingException('Can only add weight once')

        if obj.child is not None:
            return self._validate(obj.child, func, funclist)

        return True

    def _validate_func_exits_once(self, func):
        top_node = self._find_top_parent()
        self._validate(top_node, func, funclist=[])

    def update_text_str(self,new_str):
        self.text = new_str
        if self.parent is not None:
            self.parent.update_text_str(new_str)

    @staticmethod
    def get_class_by_func_name(func_name):
        if func_name == 'text':
            class_name = 'Text'
        elif func_name == 'nospace':
            class_name = 'NoSpace'
        else:
            first_letter = func_name[0].upper()
            class_name = first_letter + func_name[1:] + 'Text'
        return class_name

    def init_class_by_name(self, func, text_str=None):

        self._validate_func_exits_once(func)

        if text_str is None:
            text_str = self.text_str

        module = __import__(self.__module__)
        class_name = self.get_class_by_func_name(func)
        cls = getattr(module, class_name)(text_str)
        child = self._find_last_child()
        child.child = cls
        child.child.parent = self

        return self.child

    def strikethrough(self):
        return self.init_class_by_name('strikethrough')

    def italic(self):
        return self.init_class_by_name('italic')

    def inlinecode(self):
        return self.init_class_by_name('inlinecode')

    def bold(self):
        return self.init_class_by_name('bold')

    def important(self):
        return self.init_class_by_name('important')

    def to_text(self):
            if type(self) == NoSpace:
                new_obj = NoSpace(self.text_str)
            else:
                new_obj = Text(self.text_str)
            if self.child is not None:
                if type(self.child) is not Text or type(self.child) is not NoSpace :
                    self.child = new_obj
                    return self.child.to_text()
            else:
                return new_obj
            self.parent=None
            return self


    def __str__(self):
        return self.text_str


class TextFormater(StringFormater):

    def __init__(self, text_str, formatsign):
        super().__init__(text_str)
        self.text = text_str
        self.formatsign = formatsign

    def _render(self):
        master_parent = self._find_top_parent(self)
        return self._render_top_parent_and_child(master_parent)

    def _render_top_parent_and_child(self, obj, acc_str: str = ''):
        acc_str = acc_str + obj.formatsign
        if obj.child is not None:
            return self._render_top_parent_and_child(obj.child, acc_str)
        return_str = acc_str + obj.__str__() + acc_str[::-1]
        return return_str

    def __str__(self):
        return self.text


class NoSpace(TextFormater):
    def __init__(self, text_str: str = None):
        super().__init__(text_str, formatsign='')

    def __getattr__(self, item):
        if item in list(filter(lambda func: '__' not in func, dir(Document))):
            raise FormatingException(f"Cannot add {item} to nospace!")


class StrikethroughText(TextFormater):
    def __init__(self, text_str):
        super().__init__(text_str=text_str, formatsign='~~')


class ItalicText(TextFormater):
    def __init__(self, text_str):
        super().__init__(text_str, formatsign='*')


class Text(TextFormater):
    def __init__(self, text_str: str):
        super().__init__(text_str, formatsign='')


class BoldText(TextFormater):
    def __init__(self, text_str):
        super().__init__(text_str, formatsign='**')


class InlinecodeText(TextFormater):
    def __init__(self, text_str):
        super().__init__(text_str, formatsign='`')

class ImportantText(TextFormater):
    def __init__(self,text_str):
        super().__init__(text_str, formatsign='==')

class HorizaontalRule(Formater):
    def __init__(self):
        super().__init__()

    def _render(self):
        return '\n---\n'


class Break(Formater):
    def __init__(self):
        super().__init__()

    @staticmethod
    def render():
        return '<br/>'


class Heading(Formater):

    def __init__(self, text, size=1):
        super().__init__()
        self.size = size
        self.text = text

    def _render(self):
        return '\n' + ''.join(['#' for _ in range(0, self.size)]) + f' {self.text}\n'


class Table(Formater):
    def __init__(self, headers: Iterable):
        super().__init__()
        self.headers = self._entry_to_doc_text(headers)
        self.rows = []


    def _entry_to_doc_text(self, entries,parent_feature=None):
        for i, entry in enumerate(entries):

            if type(entry) == str:
                new_entry = DocText().nospace(entry)
                new_entry.parent_feature = parent_feature

            elif type(entry)==DocText:
                new_entry = entry
                new_entry.parent_feature=parent_feature
            else:
                new_entry = DocText().nospace(str(entry))
                new_entry.parent_feature = parent_feature
            entries[i] = new_entry
        return entries

    def add_row(self,values:Iterable,index=None):
        if len(self.headers)!= len(values):
            raise FormatingException("Cannot add row with a size not matching size of headers")
        else:
            rows = self._entry_to_doc_text(values,Table)
            if index is not None:
                self.rows.insert(index, rows)
            else:
                self.rows.append(rows)

        return self

    def _join_row(self,acc_row,new_col,last_col=False):
        acc_row = acc_row + '|%s' % new_col._render() if type(new_col) == DocText else new_col
        if last_col:
            acc_row = acc_row + '|\n'
        return acc_row

    def _get_second_rows_count(self,rows):

        longest_word_count = [0 for _ in range(0, len(self.headers))]
        wordcounts = []
        for row in rows:
            for word in row:
                rendered_content = word._render()
                wordcounts.append(len(rendered_content))


        for wordcount in wordcounts:
            for index, value in enumerate(longest_word_count):
                if wordcount > value:
                    longest_word_count[index] = wordcount
        return longest_word_count

    def _create_second_row(self,largest_columns):

        column_list = []
        for col in largest_columns:
            dashes_string = ''
            dashes = ['-' for _ in range(0,col)]
            dashes_string=dashes_string.join(dashes)
            column_list.append(DocText().nospace(dashes_string))
        return column_list

    def _add_space_amount(self, col_max, word):

        space_amount = col_max-len(word._render())
        word.render_spaces=space_amount
        return word

    def _render(self):
        self.add_row(self.headers, 0)
        wordcounts = self._get_second_rows_count(self.rows)
        second_row = self._create_second_row(wordcounts)
        self.add_row(second_row,1)

        text_rows = ''
        for row in self.rows:
            for col_index, column in enumerate(row):
                self._add_space_amount(wordcounts[col_index],column)
                text_rows = self._join_row(text_rows,column,True if col_index==len(row)-1 else False)

        return '\n\n'+text_rows+'\n'





