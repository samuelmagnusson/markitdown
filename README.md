
# Markitdown


This is a markdown generation framework aimed for creating reports 
or other auto-generated documents. It supports the following text features: 




|Feature          |Example          |
|-----------------|-----------------|
|Bold text        |**Example**      |
|Italic text      |*Example*        |
|Inline code text |`Example`        |
|Strikethrou text |~~Example~~      |
|Multiple weights |***~~Example~~***|



It is also possible to ad a quote: 



>  This is a awsome quote

or a code block: 



```

    
    features_examples=[
            ["Bold text",DocText().bold("Example")],
            ["Italic text", DocText().italic("Example")],
            ["Inline code text", DocText().inlinecode("Example")],
            ["Strikethrou text", DocText().strikethrough("Example")],
            ["Multiple weights", DocText().text("Example").bold().italic().strikethrough()]
        ]
    
        for example in features_examples:
            table.add_row(example)
    
```


It is also possible to use lists: 



- Välling
- Choklad
- **Margarin**





1. Välling
2. Choklad
3. **Margarin**
	- Kanin
	- Björn
	- koala
4. Kött
