from markitdown import Document, DocText, FormatingException


def test_generate_document_with_text():
    md = Document().text("jag har gula byxor").render_document_text()
    assert md == ' jag har gula byxor'


def test_chain_weights():
    md = Document().text("jag har gula byxor").bold("SOM ÄR JÄTTESKÖNA").render_document_text()
    assert md == ' jag har gula byxor **SOM ÄR JÄTTESKÖNA**'


def test_add_quote():
    md = Document().text("jag har kollat på alla avsnitt av friends!")\
        .quote(DocText().text("gröna sköna sommar")).text("nu är det slut!").render_document_text()
    assert md == ' jag har kollat på alla avsnitt av friends!\n\n>  gröna sköna sommar\n\nnu är det slut!'

def test_add_quote_with_doctext_containing_nospace_with_text():
    md = Document().quote(DocText().bold("greta").nospace("-GRIS").bold("har gula ögon").nospace("-lock")).render_document_text()
    assert md == "\n\n>  greta-GRIS har gula ögon-lock"

def test_add_checkbox_with_doc_text():
    md = Document().text("jag har kollat på alla avsnitt av friends!")\
        .checkbox(DocText().text("gröna sköna sommar")).render_document_text()
    assert md == ' jag har kollat på alla avsnitt av friends! \n - [ ]  gröna sköna sommar'


def test_add_checkbox_with_text():
    md = Document().text("jag har kollat på alla avsnitt av friends!")\
        .checkbox("gröna sköna sommar").render_document_text()
    assert md == ' jag har kollat på alla avsnitt av friends! \n - [ ]  gröna sköna sommar'


def test_add_checkbox_with_bold_text():
    md = Document().text("jag har kollat på alla avsnitt av friends!").checkbox("gröna sköna sommar").bold()\
        .render_document_text()
    assert md == ' jag har kollat på alla avsnitt av friends! \n - [ ]  **gröna sköna sommar**'


def test_add_checkbox_with_bold_text_and_following_new_text():
    md = Document().text("jag har kollat på alla avsnitt av friends!")\
        .checkbox("gröna sköna sommar").bold().text("Jag vill äta mat!").render_document_text()
    assert md == (' jag har kollat på alla avsnitt av friends! \n'
                  ' - [ ]  **gröna sköna sommar**\n'
                  '\n'
                  'Jag vill äta mat!')


def test_multiple_checkboxes():
    md = Document().checkbox(DocText().text("first").bold())\
        .checkbox("second").checkbox("third").italic().render_document_text()
    assert md == ' \n - [ ]  **first** \n - [ ]  second \n - [ ]  *third*'


def test_ordered_list():
    md = Document().ordered_list().add_item("I").add_item("hate").add_item("you").render_document_text()
    assert md == '\n\n1. I\n2. hate\n3. you\n'


def test_unordered_list():
    md = Document().unordered_list().add_item("I").add_item("hate").add_item("you").render_document_text()
    assert md == '\n\n- I\n- hate\n- you\n'


def test_ordered_list_with_unordered_list():
    md = Document().ordered_list().add_item("I").add_item("Hate:") \
        .unordered_list().add_item("Banana").add_item("Chocklate").render_document_text()
    assert md == '\n\n1. I\n2. Hate:\n\t- Banana\n\t- Chocklate\n'


def test_cannot_add_item_after_calling_parent_document_function():
    ordered_list = Document().ordered_list()
    ordered_list.add_item("grönsak").text("Jag vill inte ha korv!")
    try:
        ordered_list.add_item("kaffe")
        assert False
    except FormatingException:
        assert True


def test_proper_numbering_after_continue_ordered_list_after_adding_sub_lists():
    md = Document().ordered_list().add_item("First").add_item("Second").ordered_list().add_item("Sublist first"). \
          add_item("Sublist Second").get_parent().add_item("Third").render_document_text()
    assert md == '\n\n1. First\n2. Second\n\t1. Sublist first\n\t2. Sublist Second\n3. Third\n'


def test_nested_list_in_five_steps():
    md = Document().ordered_list().add_item("item1")\
        .ordered_list().add_item("item2").unordered_list().add_item("item3")\
        .unordered_list().add_item("item4").ordered_list().add_item("item5").get_parent().add_item("item4.2") \
        .get_parent().add_item("item3.2").get_parent()\
        .add_item("item2.2").get_parent().add_item("item2.1").render_document_text()
    assert md == "\n\n1. item1\n\t1. item2\n\t\t- item3\n\t\t\t- item4\n\t\t\t\t1."\
                 " item5\n\t\t\t- item4.2\n\t\t- item3.2\n\t2. item2.2\n2. item2.1\n"


def test_add_list_with_formated_text():
    md = Document().ordered_list().add_item(DocText().text("jag har gröna byxor").bold().italic())\
        .add_item("item2").unordered_list().add_item(DocText().inlinecode("jag finns!")).render_document_text()
    assert md == "\n\n1. ***jag har gröna byxor***\n2. item2\n\t- `jag finns!`\n"


def test_fenced_code_block_short_text():
    md = Document().fenced_code_block("Jag är gul").render_document_text()
    assert md == '\n\n```\nJag är gul\n```\n'


def test_fenced_code_block_long_text():
    md = Document().fenced_code_block("Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul" 
                                      " Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul"
                                      " Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul"
                                      " Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul"
                                      " Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul"
                                      " Jag är gul ").render_document_text()
    assert md ==('\n'
 '\n'
 '```\n'
 'Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul '
 'Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul '
 'Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul '
 'Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul '
 'Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul Jag är gul '
 'Jag är gul \n'
 '```\n')


def test_fenced_code_block_with_doc_text():
    md = Document().fenced_code_block(DocText().text(
        "Jag har gröna byxor").bold()).render_document_text()
    assert md == '\n\n```\nJag har gröna byxor\n```\n'

def test_table():
    md = (((Document().table(["key","value"]).
          add_row([DocText().bold("APA"),DocText().strikethrough("Kanin")])).
          add_row(["göran","gudrun"])).
          add_row([12312,3332])).get_parent().text("Nu är tabellen slut!").render_document_text()
    assert md == "\n\n|key       |value     |\n|----------|----------|\n| "\
           "**APA**  | ~~Kanin~~|\n|göran     |gudrun    |\n|12312     |3332      |\n\nNu är tabellen slut!"