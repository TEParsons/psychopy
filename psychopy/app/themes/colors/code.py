from pygments.style import Style, Token


__all__ = [
    "BaseCodeColors",
    "allCodeColorSchemes",
]


# global variable to keep track of all known code color schemes
# this will be appended to whenever BaseAppColors is subclassed
allCodeColorSchemes = []


class BaseCodeColorScheme(Style):
    """
    PsychoPy `CodeColors` objects are mostly the same as pygments `Style`s, with a few extra keys 
    to indicate colors for the UI around a text editor, as well as the subclassing behaviour which 
    stores all code color schemes.
    """
    # a general color scheme for ease of reference
    scheme = {
        # three shades of background color
        'crust': "#e3e3e3",
        'mantle': "#f2f2f2",
        'base': "#ffffff",
        # text colors (against background & against highlight)
        'text': "#000000",
        'hltext': "#ffffff",
        # some general colors
        'grey': "#66666e",
        'blue': "#02a9ea",
        'green': "#6ccc74",
        'yellow': "#f1d302",
        'orange': "#ec9703",
        'red': "#f2545b",
        'lavender': "#c3bef7",
    }

    # parameters for the text control itself
    background_color = scheme['base']
    highlight_color = scheme['crust']
    line_number_color = scheme['text']
    line_number_background_color = scheme['mantle']
    line_number_special_color = scheme['hltext']
    line_number_special_background_color = scheme['red']

    # style definitions for individual token types
    styles = {
        # default style
        Token: f"{scheme['text']} mono",
        # regular text
        Token.Text: scheme['text'],
        Token.Text.Whitespace: scheme['mantle'],
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
        Token.Literal.String.Doc: scheme['crust'],
        Token.Literal.String.Escape: scheme['text'],
        # Token.Literal.String.Regex: "inherit",
        # numbers
        Token.Literal.Number: scheme['blue'],
        # markdown
        Token.Generic.Heading: f"{scheme['red']} bold",
        Token.Generic.Subheading: f"{scheme['blue']} bold",
        # Token.Generic.Deleted: "inherit",
        # console
        Token.Generic.Output: scheme['text'],
        Token.Generic.Error: scheme['red'],
        Token.Generic.Traceback: scheme['red'],
        Token.Error: scheme['red'],
        # declarations (def, class, etc.)
        Token.Keyword.Declaration: f"{scheme['red']} bold",
        Token.Keyword.Reserved: f"{scheme['blue']} bold italic",
    }



class PsychoPyLight(BaseCodeColorScheme):
    # PsychoPy Light is the default, so doesn't need any change from base
    pass


class PsychoPyDark(BaseCodeColorScheme):
    # a general color scheme for ease of reference
    scheme = {
        # backgrounds
        'crust': "#57575f",
        'mantle': "#66666e",
        'base': "#7f7f7d",
        # text
        'text': "#ffffff",
        'hltext': "#ffffff",
        # colors
        'grey': "#acacb0",
        'blue': "#02a9ea",
        'green': "#6ccc74",
        'yellow': "#f1d302",
        'orange': "#ec9703",
        'red': "#f2545b",
        'lavender': "#c3bef7",
    }
    # PsychoPy Light is the default, so doesn't need any change from base
    # parameters for the text control itself
    background_color = scheme['base']
    highlight_color = scheme['crust']
    line_number_color = scheme['text']
    line_number_background_color = scheme['mantle']
    line_number_special_color = scheme['hltext']
    line_number_special_background_color = scheme['red']

    # style definitions for individual token types
    styles = {
        # default style
        Token: f"{scheme['text']} mono",
        # regular text
        Token.Text: scheme['text'],
        Token.Text.Whitespace: scheme['mantle'],
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
        Token.Literal.String.Doc: scheme['crust'],
        Token.Literal.String.Escape: scheme['text'],
        # Token.Literal.String.Regex: "inherit",
        # numbers
        Token.Literal.Number: scheme['blue'],
        # markdown
        Token.Generic.Heading: f"{scheme['red']} bold",
        Token.Generic.Subheading: f"{scheme['blue']} bold",
        # Token.Generic.Deleted: "inherit",
        # console
        Token.Generic.Output: scheme['text'],
        Token.Generic.Error: scheme['red'],
        Token.Generic.Traceback: scheme['red'],
        Token.Error: scheme['red'],
        # declarations (def, class, etc.)
        Token.Keyword.Declaration: f"{scheme['red']} bold",
        Token.Keyword.Reserved: f"{scheme['blue']} bold italic",
    }