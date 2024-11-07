from markitdown import Document, DocText

document = Document(file_name="README.md",file_path='../')

document.heading("Markitdown")

document.text("This is a markdown generation "
              "framework aimed for creating reports or other auto-generated documents.")
document.text("It supports the following text features: ")
table = document.table(["Feature","Example"])

features_examples=[
    ["Bold text",DocText().nospace().bold("Example")],
    ["Italic text", DocText().nospace().italic("Example")],
    ["Inline code text", DocText().nospace().inlinecode("Example")],
    ["Strikethrou text", DocText().nospace().strikethrough("Example")],
    ["Multiple weights", DocText().nospace().text("Example").bold().italic().strikethrough()]
]

for example in features_examples:
    table.add_row(example)

code_block="""
    
    features_examples=[
            ["Bold text",DocText().bold("Example")],
            ["Italic text", DocText().italic("Example")],
            ["Inline code text", DocText().inlinecode("Example")],
            ["Strikethrou text", DocText().strikethrough("Example")],
            ["Multiple weights", DocText().text("Example").bold().italic().strikethrough()]
        ]
    
        for example in features_examples:
            table.add_row(example)
    """
(document.text("It is also possible to ad a quote: ").quote("This is a awsome quote").text("or a code block: ")
 .fenced_code_block(code_block))


shopping_list = ["Välling","Choklad",DocText().text("Margarin").bold()]
document.text("It is also possible to use lists: ")

unordered_list = document.unordered_list()
ordered_list = document.ordered_list()
for thing in shopping_list:
   unordered_list.add_item(thing)
   ordered_list.add_item(thing)

ordered_list.unordered_list().add_item("Kanin").add_item("Björn").add_item("koala").get_parent() \
    .add_item("Kött")
document.store_document()