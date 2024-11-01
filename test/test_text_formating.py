from markitdown import Text, BoldText, ItalicText, InlinecodeText, StrikethroughText, FormatingException, DocText


def test_bold():
    assert BoldText("hej")._render() == "**hej**"
def test_italic():
    assert ItalicText("hej")._render() == "*hej*"
def test_inlinecode():
    assert InlinecodeText("hej")._render() == "`hej`"
def test_strikethrough():
    assert StrikethroughText("hej")._render() == '~~hej~~'
def test_str_format_text_bold():
    assert Text("hoppla").bold()._render() == '**hoppla**'
def test_str_format_text_text():
    assert Text("hoppla").to_text()._render() == 'hoppla'
def test_str_format_text_italic():
    assert Text("hoppla").italic()._render() == '*hoppla*'
def test_str_format_text_inlinecode():
    assert Text("hoppla").inlinecode()._render() == '`hoppla`'
def test_str_chaining_bold_strikethrough():
    assert Text("hoppla").bold().strikethrough()._render() == '**~~hoppla~~**'
def test_str_chaining_italic_bold():
    assert Text("hopplao").italic().bold()._render() == '***hopplao***'
def test_str_chainging_bold_italic_bold():
    try:
        Text("hoppla").bold().italic().bold()
        assert False
    except FormatingException as e:
        assert str(e) == 'Can only add weight once'
        assert True

def test_str_chainging_bold_bold_italic():
    try:
        Text("hoppla").bold().bold().italic()
        assert False
    except FormatingException as e:
        assert str(e) == 'Can only add weight once'
        assert True

def test_bold_to_bold():
    try:
        BoldText("hoppla").bold()
        assert False
    except FormatingException as e:
        assert str(e) == 'Can only add weight once'
        assert True

def test_simple_document():
    md = DocText().text("mjau").strikethrough().inlinecode().bold().italic()._render()
    assert md == ' `mjau`'

def test_simple_document_with_new_text_after_inline_code():
    md = DocText().text("mjau").strikethrough().inlinecode().bold().italic().text("jag vill inte ha hund")._render()
    assert md == ' `mjau` jag vill inte ha hund'


def test_simple_document_with_several_texts():
    md = DocText().text("mjau").strikethrough("voff").bold("kakaka").italic("muuu").inlinecode("bäää")._render()
    assert md ==' mjau ~~voff~~ **kakaka** *muuu* `bäää`'

def test_simple_document_add_same_weight_to_different_texts():
    md = DocText().text("mjau").bold().text("bäää").bold()._render()
    assert md == ' **mjau** **bäää**'

def test_inital_nospace():
    md = DocText().nospace().text("fjoff")._render()
    assert md == 'fjoff'

def test_inital_nospace_with_chained_weights():
    md = DocText().nospace().text("fjoff").bold()._render()
    assert md == '**fjoff**'

def test_nospace_between_objects():
    md = DocText().bold("fjoff").nospace().text("jag är en åsna").bold()._render()
    assert md == ' **fjoff****jag är en åsna**'

def test_nospace_in_beginning_and_between_objects():
    md = DocText().nospace().bold("fjoff").nospace().text("jag är en åsna").bold()._render()
    assert md == '**fjoff****jag är en åsna**'
def test_nospace_in_end():
    md = DocText().nospace().bold("fjoff").text("jag är en åsna").bold().nospace()._render()
    assert md == '**fjoff** **jag är en åsna**'

def test_add_weight_to_nospace():
        md = DocText().nospace().bold().text("jag är en åsna").bold()._render()
        assert md=='**jag är en åsna**'

def test_add_bold_to_nospace_with_new_bold():
    md = DocText().bold("jag bru").nospace("kar").nospace().bold("kavla")._render()
    assert md == ' **jag bru**kar**kavla**'

def test_add_bold_to_nospace_with_italic():
    md = DocText().bold("jag bru").nospace("kar").italic().nospace().bold("kavla")._render()
    assert md == ' **jag bru***kar***kavla**'

def test_doctest_with_nospace_containing_text():
    md = DocText().bold("jajjemensan").nospace("jag har gula ögon").bold("jaga").nospace("katt")._render()
    assert md ==' **jajjemensan**jag har gula ögon **jaga**katt'

def test_text_bold():
    md = DocText().text("Jag har gröna byxor").bold().italic().nospace().bold("korv").nospace("göran").strikethrough().inlinecode()._render()
    assert md == " ***Jag har gröna byxor*****korv**`göran`"
