from markitdown import Document, DocText

document = Document(file_name="README.md",file_path='../')

document.heading("Markitdown")

document.text("This is a markdown generation "
              "framework aimed for creating reports or other auto-generated documents")
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
(document.text("It is also possible to a quote: ").quote("This is a awsome quote").text("or a code block")
 .fenced_code_block(code_block))


document.store_document()