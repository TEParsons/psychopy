from psychopy.preferences import prefs
import wx.stc as stc
from pygments.style import Style, Token


__all__ = [
    "BaseCodeColors",
    "allCodeColorSchemes",
]


# mapping of stc tags (which wx requires for styling) to pygments tokens (which we use for themes)
stc2pygments = {
    stc.STC_STYLE_DEFAULT: Token,
    stc.STC_STYLE_LINENUMBER: Token,
    stc.STC_STYLE_INDENTGUIDE: Token.Text.Whitespace,
    stc.STC_STYLE_BRACELIGHT: Token.Text.Whitespace,
    stc.STC_STYLE_CONTROLCHAR: Token.Keyword,
    # Python
    stc.STC_P_OPERATOR: Token.Operator,
    stc.STC_P_WORD: Token.Keyword,
    stc.STC_P_WORD2: Token.Keyword.Type,
    stc.STC_P_IDENTIFIER: Token.Name,
    stc.STC_P_NUMBER: Token.Number,
    stc.STC_P_CHARACTER: Token.Literal.String.Char,
    stc.STC_P_STRING: Token.Literal.String,
    stc.STC_P_STRINGEOL: Token.Literal.String.Escape,
    stc.STC_P_DECORATOR: Token.Name.Decorator,
    stc.STC_P_DEFNAME: Token.Name.Function,
    stc.STC_P_CLASSNAME: Token.Name.Class,
    stc.STC_P_COMMENTLINE: Token.Comment,
    stc.STC_P_COMMENTBLOCK: Token.Comment.Multiline,
    stc.STC_P_TRIPLE: Token.Literal.String.Doc,
    stc.STC_P_TRIPLEDOUBLE: Token.Literal.String.Doc,
    stc.STC_P_DEFAULT: Token,
    # # R
    # stc.STC_R_OPERATOR: Token.,
    # stc.STC_R_BASEKWORD: Token.,
    # stc.STC_R_KWORD: Token.,
    # stc.STC_R_IDENTIFIER: Token.,
    # stc.STC_R_NUMBER: Token.,
    # stc.STC_R_STRING2: Token.,
    # stc.STC_R_STRING: Token.,
    # stc.STC_R_INFIX: Token.,
    # stc.STC_R_INFIXEOL: Token.,
    # stc.STC_R_COMMENT: Token.,
    # stc.STC_R_DEFAULT: Token.,
    # # C++
    # stc.STC_C_OPERATOR: Token.,
    # stc.STC_C_WORD: Token.,
    # stc.STC_C_WORD2: Token.,
    # stc.STC_C_IDENTIFIER: Token.,
    # stc.STC_C_NUMBER: Token.,
    # stc.STC_C_CHARACTER: Token.,
    # stc.STC_C_STRING: Token.,
    # stc.STC_C_STRINGEOL: Token.,
    # stc.STC_C_GLOBALCLASS: Token.,
    # stc.STC_C_COMMENT: Token.,
    # stc.STC_C_COMMENTLINE: Token.,
    # stc.STC_C_COMMENTDOCKEYWORD: Token.,
    # stc.STC_C_COMMENTDOCKEYWORDERROR: Token.,
    # stc.STC_C_COMMENTLINEDOC: Token.,
    # stc.STC_C_COMMENTDOC: Token.,
    # stc.STC_C_DEFAULT: Token.,
    # stc.STC_C_PREPROCESSOR: Token.,
    # stc.STC_C_PREPROCESSORCOMMENT: Token.,
    # # JSON
    # stc.STC_JSON_OPERATOR: Token.,
    # stc.STC_JSON_KEYWORD: Token.,
    # stc.STC_JSON_URI: Token.,
    # stc.STC_JSON_COMPACTIRI: Token.,
    # stc.STC_JSON_ERROR: Token.,
    # stc.STC_JSON_ESCAPESEQUENCE: Token.,
    # stc.STC_JSON_PROPERTYNAME: Token.,
    # stc.STC_JSON_LDKEYWORD: Token.,
    # stc.STC_JSON_NUMBER: Token.,
    # stc.STC_JSON_STRING: Token.,
    # stc.STC_JSON_STRINGEOL: Token.,
    # stc.STC_JSON_LINECOMMENT: Token.,
    # stc.STC_JSON_BLOCKCOMMENT: Token.,
    # stc.STC_JSON_DEFAULT: Token.,
    # # Markdown
    # stc.STC_MARKDOWN_DEFAULT: Token.,
    # stc.STC_MARKDOWN_LINE_BEGIN: Token.,
    # stc.STC_MARKDOWN_BLOCKQUOTE: Token.,
    # stc.STC_MARKDOWN_CODE: Token.,
    # stc.STC_MARKDOWN_CODE2: Token.,
    # stc.STC_MARKDOWN_EM1: Token.,
    # stc.STC_MARKDOWN_EM2: Token.,
    # stc.STC_MARKDOWN_STRONG1: Token.,
    # stc.STC_MARKDOWN_STRONG2: Token.,
    # stc.STC_MARKDOWN_HEADER1: Token.,
    # stc.STC_MARKDOWN_HEADER2: Token.,
    # stc.STC_MARKDOWN_HEADER3: Token.,
    # stc.STC_MARKDOWN_HEADER4: Token.,
    # stc.STC_MARKDOWN_HEADER5: Token.,
    # stc.STC_MARKDOWN_HEADER6: Token.,
    # stc.STC_MARKDOWN_HRULE: Token.,
    # stc.STC_MARKDOWN_LINK: Token.,
    # stc.STC_MARKDOWN_OLIST_ITEM: Token.,
    # stc.STC_MARKDOWN_PRECHAR: Token.,
    # stc.STC_MARKDOWN_ULIST_ITEM: Token.,
}



class BaseCodeColorScheme(Style):
    """
    PsychoPy `CodeColors` objects are mostly the same as pygments `Style`s, with a few extra keys 
    to indicate colors for the UI around a text editor, as well as the subclassing behaviour which 
    stores all code color schemes.
    """
    # a general color scheme for ease of reference
    scheme = {
        # four shades of background color
        'overlay': "#d4d4d4",
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

    # font family
    font_family = "JetBrains Mono"

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
        Token.Literal.String.Doc: scheme['grey'],
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
        Token.Generic.Warning: scheme['orange'],
        Token.Generic.Error: scheme['red'],
        Token.Generic.Traceback: scheme['red'],
        Token.Error: scheme['red'],
        # declarations (def, class, etc.)
        Token.Keyword.Declaration: f"{scheme['red']} bold",
        Token.Keyword.Reserved: f"{scheme['blue']} bold italic",
    }

    # dict that's updated with wx.Font objects when one is created for a given style
    _stcCache = {}

    @classmethod
    def wxFontForToken(cls, token):
        """
        Get the wx font described by a pygments style.

        Parameters
        ----------
        token : pygments.token.Token
            Token to get wx font for

        Returns
        -------
        wx.richtext.TextAttr
            TextAttr object describing the pygments style
        """
        import wx, wx.richtext

        if token not in cls._stcCache:
            # get pygments style for token
            pygStyle = cls.style_for_token(token)
            # convert to a wx.TextAttr object
            font = wx.richtext.RichTextAttr()
            font.SetFontPointSize(int(prefs.coder['codeFontSize']))
            font.SetFontFaceName(cls.font_family)
            font.SetTextColour("#" + pygStyle['color'])
            if pygStyle['bgcolor']:
                font.SetBackgroundColour("#" + pygStyle['bgcolor'])
            else:
                font.SetBackgroundColour(cls.background_color)
            font.SetFontWeight(wx.FONTWEIGHT_BOLD if pygStyle['bold'] else wx.FONTWEIGHT_NORMAL)
            font.SetFontStyle(wx.FONTSTYLE_ITALIC if pygStyle['italic'] else wx.FONTSTYLE_NORMAL)
            font.SetFontUnderlined(pygStyle['underline'])
            # cache
            cls._stcCache[token] = font

        return cls._stcCache[token]

    def __init_subclass__(cls):
        # store base style
        cls.base = cls.wxFontForToken(Token)


class PsychoPyLight(BaseCodeColorScheme):
    # PsychoPy Light is the default, so doesn't need any change from base
    pass


class PsychoPyDark(BaseCodeColorScheme):
    # a general color scheme for ease of reference
    scheme = {
        # backgrounds
        'overlay': "#66666e",
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
        Token.Literal.String.Doc: scheme['grey'],
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