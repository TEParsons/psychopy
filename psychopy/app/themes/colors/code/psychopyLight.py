from psychopy.app.themes.colors.code import CodeColors, Token


scheme = {
    'black': "#000000",
    'offblack': "#161616",
    'grey': "#66666e",
    'lightgrey': "#acacb0",
    'offwhite': "#f2f2f2",
    'white': "#ffffff",
    'red': "#f2545b",
    'blue': "#02a9ea",
    'green': "#6ccc74",
    'orange': "#ec9703",
    'yellow': "#f1d302",
    'lavender': "#c3bef7",
}


class PsychopyLight(CodeColors):
    # parameters for the text control itself
    background_color = scheme['white']
    highlight_color = scheme['lightgrey']
    line_number_color = scheme['black']
    line_number_background_color = scheme['offwhite']
    line_number_special_color = scheme['white']
    line_number_special_background_color = scheme['red']

    #: Style definitions for individual token types.
    styles = {
        # default style
        Token: f"{scheme['black']} mono",
        # regular text
        Token.Text: scheme['black'],
        Token.Text.Whitespace: scheme['offwhite'],
        # comments
        Token.Comment: scheme['green'],
        # Token.Comment.Multiline: "inherit",
        # keywords
        Token.Keyword: scheme['red'],
        Token.Keyword.Type: f"{scheme['blue']} italic",
        # operators (+-/*=)
        # Token.Operator: "inherit",
        # Token.Punctuation: "inherit",
        # names
        Token.Name.Builtin: f"{scheme['red']} bold",
        # Token.Name.Function: "inherit",
        # Token.Name.Class: "inherit",
        # Token.Name.Exception: "inherit",
        # Token.Name.Variable: "inherit",
        # Token.Name.Constant: "inherit",
        # Token.Name.Attribute: "inherit",
        Token.Name.Decorator: scheme['orange'],
        # strings
        Token.Literal.String: scheme['grey'],
        Token.Literal.String.Doc: scheme['lightgrey'],
        Token.Literal.String.Escape: scheme['black'],
        # Token.Literal.String.Regex: "inherit",
        # numbers
        Token.Literal.Number: scheme['blue'],
        # markdown
        Token.Generic.Heading: f"{scheme['red']} bold",
        Token.Generic.Subheading: f"{scheme['blue']} bold",
        # Token.Generic.Deleted: "inherit",
        # console
        Token.Generic.Output: scheme['black'],
        Token.Generic.Error: scheme['red'],
        Token.Generic.Traceback: scheme['red'],
        Token.Error: scheme['red'],
        # declarations (def, class, etc.)
        Token.Keyword.Declaration: f"{scheme['red']} bold",
        Token.Keyword.Reserved: f"{scheme['blue']} bold italic",
    }
