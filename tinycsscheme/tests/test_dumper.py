"""
    Tests for the CSScheme dumper
"""

import pytest

from ..tinycss.css21 import Stylesheet, Declaration, RuleSet
from ..tinycss.token_data import Token
from ..tinycss.tokenizer import tokenize_grouped

from .. import dumper
from ..dumper import DumpError
from ..parser import StringRule

from . import jsonify


# Shorthand functions for tinycss classes
def T(type_, value):  # noqa
    return Token(type_, value, value, None, 0, 0)


def SR(keyword, value):  # noqa
    tokens = list(tokenize_grouped(value))
    assert len(tokens) == 1
    return StringRule(keyword, tokens[0], 0, 0)


def SS(rules):  # noqa
    return Stylesheet(rules, [], None)


def RS(sel, decl, at_rules=[]):  # noqa
    sel = tokenize_grouped(sel)
    rs = RuleSet(sel, decl, 0, 0)
    rs.at_rules = at_rules
    return rs


def DC(name, value):  # noqa
    return Declaration(name, tokenize_grouped(value), None, 0, 0)


@pytest.mark.parametrize(('stylesheet', 'expected_data'), [
    (SS([SR('@name', "Test"),
         SR('@at-rule', "hi"),
         RS('*', []),
         # Should this be tested here?
         RS('source', [DC('foreground', "#123456")]),
         SR('@uuid', '2e3af29f-ebee-431f-af96-72bda5d4c144')
         ]),
     {'name': "Test",
      'at-rule': "hi",
      'uuid': "2e3af29f-ebee-431f-af96-72bda5d4c144",
      'settings': [
          {'settings': {}},
          {'scope': "source",
           'settings': {'foreground': "#123456"}},
      ]}
     ),
])
def test_datafy(stylesheet, expected_data):
    data = dumper.datafy_stylesheet(stylesheet)
    assert data == expected_data


@pytest.mark.parametrize(('stylesheet', 'expected_error'), [
    (SS([SR('@name', "Test"),
         ]),
     "Must contain '*' ruleset"
     ),

    (SS([SR('@name', "Test"),
         RS('*', []),
         RS('*', [])
         ]),
     "Only one *-rule allowed"
     ),

    (SS([SR('@settings', "value"),
         SR('@name', "Test"),
         RS('*', [])
         ]),
     "Can not override 'settings' key using at-rules."
     ),
])
def test_datafy_errors(stylesheet, expected_error):
    try:
        dumper.datafy_stylesheet(stylesheet)
        assert False, "no exception was raised"
    except DumpError as e:
        assert expected_error in str(e)


@pytest.mark.parametrize(('ruleset', 'expected_data'), [
    # declarations
    (RS('*', [DC('foreground',  "#123456"),
              DC('someSetting', "yeah"),
              DC('anInteger',   "2"),
              # Test if subcalls (translate_colors) function properly
              DC('another',     "rgb(0,0,0)"),
              ],
        []),
     {'settings': {
         'foreground':  "#123456",
         'someSetting': "yeah",
         'anInteger':   "2",  # converted to string
         'another':     "#000000",
     }}
     ),

    # string rules
    (RS("source",
        [DC('fontStyle', "bold"),
         ],
        [SR('@name', "\"Test name\""),
         SR('@arbitrary', "\"just some string\"")
         ]),
     {'name': "Test name",
      'arbitrary': "just some string",
      'scope': "source",
      'settings': {
          'fontStyle': "bold",
      }}
     ),

    # whitespace stripping of selector
    (RS("some    other \nruleset with.blank.lines",
        []),
     {'scope': "some other ruleset with.blank.lines",
      'settings': {
      }}
     ),

    # escaped subtract operator (with legacy test)
    (RS("not '-' subtract, real \- subtract",
        []),
     {'scope': "not '-' subtract, real - subtract",
      'settings': {
      }}
     ),

    # other escaped operators
    (RS(R"\(a \| b\) \- \(c \& b.f, j.\1\)",
        []),
     {'scope': "(a | b) - (c & b.f, j.1)",
      'settings': {
      }}
     ),
])
def test_datafy_ruleset(ruleset, expected_data):
    data = dumper.datafy_ruleset(ruleset)
    assert data == expected_data


@pytest.mark.parametrize(('ruleset', 'expected_error'), [
    (RS('*',
        [],
        [SR('@settings', "a"),
         ]),
     "You can not override the 'settings' key using at-rules"
     ),
    (RS('yeah', [],
        [SR('@scope', "a"),
         ]),
     "You can not override the 'scope' key using at-rules"
     ),
])
def test_datafy_ruleset_errors(ruleset, expected_error):
    try:
        dumper.datafy_ruleset(ruleset)
        assert False, "no exception was raised"
    except DumpError as e:
        assert expected_error in str(e)


@pytest.mark.parametrize(('decl', 'expected_decl'), [
    # pass through
    (DC('prop', "#123456 #12345678 cyan"),
     ('prop', [('HASH',  "#123456"),
               ('S',     " "),
               ('HASH',  "#12345678"),
               ('S',     " "),
               ('IDENT', "cyan")])),

    # color
    (DC('background', "#123456"),
     ('background', [('HASH', "#123456")])),

    (DC('foreground', "black"),
     ('foreground', [('HASH', "#000000")])),

    (DC('background', "cyan"),
     ('background', [('HASH', "#00FFFF")])),

    # style list
    (DC('fontStyle', 'bold italic underline'),
     ('fontStyle', [('IDENT', "bold"),
                    ('S',     " "),
                    ('IDENT', "italic"),
                    ('S',     " "),
                    ('IDENT', "underline")])),

    (DC('fontStyle', 'none'),
     ('fontStyle', [('IDENT', "")])),

    # options list
    (DC('tagsOptions', 'foreground underline squiggly_underline stippled_underline'),
     ('tagsOptions', [('IDENT', "foreground"),
                      ('S',     " "),
                      ('IDENT', "underline"),
                      ('S',     " "),
                      ('IDENT', "squiggly_underline"),
                      ('S',     " "),
                      ('IDENT', "stippled_underline")])),

    # integer
    (DC('shadowWidth', '4'),
     ('shadowWidth', [('INTEGER', 4)])),

    (DC('shadowWidth', '\"-4\"'),
     ('shadowWidth', [('STRING', "-4")])),
])
def test_validify_decl(decl, expected_decl):
    dumper.validify_declaration(decl, '')
    assert (decl.name, list(jsonify(decl.value))) == expected_decl


@pytest.mark.parametrize(('decl', 'expected_error'), [
    # color
    (DC('background', "#123456 #12345678"),
     "expected 1 token for property background, got 3"),

    (DC('background', "'hi there'"),
     "unexpected STRING token for property background"),

    (DC('bracketsForeground', "\"#12345\""),
     "unexpected STRING token for property bracketsForeground"),

    (DC('foreground', "2"),
     "unexpected INTEGER token for property foreground"),

    (DC('foreground', "not-a-color"),
     "unknown color name 'not-a-color' for property foreground"),

    # style list
    (DC('fontStyle', "#000001"),
     "unexpected HASH token for property fontStyle"),

    (DC('fontStyle', "\"hi\""),
     "unexpected STRING token for property fontStyle"),

    (DC('fontStyle', "foreground"),
     "invalid value 'foreground' for style property fontStyle"),

    (DC('fontStyle', "bold none"),
     "'none' may not be used together with other styles"),

    # options list
    (DC('tagsOptions', "#000001"),
     "unexpected HASH token for property tagsOptions"),

    (DC('bracketsOptions', "italic"),
     "invalid value 'italic' for options property bracketsOptions"),

    # integer
    (DC('shadowWidth', "1 2"),
     "expected 1 token for property shadowWidth, got 3"),
    (DC('shadowWidth', "'a'"),
     "expected number in string for property shadowWidth, got 'a'"),

    (DC('shadowWidth', "1.23"),
     "unexpected NUMBER token for property shadowWidth"),
])
def test_validify_decl_errors(decl, expected_error):
    try:
        dumper.validify_declaration(decl, '')
        assert False, "no exception was raised"
    except DumpError as e:
        assert expected_error in str(e)


@pytest.mark.parametrize(('decl', 'expected_decl'), [
    # Does not access a declaration's name, only values
    # pass through
    (DC('prop', "'hi there' #123456 ident 5"),
     ('prop', [('STRING',  "hi there"),
               ('S',       " "),
               ('HASH',    "#123456"),
               ('S',       " "),
               ('IDENT',   "ident"),
               ('S',       " "),
               ('INTEGER', 5)])),

    # changes
    (DC('prop', "'#12345678'"),
     ('prop', [('HASH', "#12345678")])),

    (DC('prop', "#123"),
     ('prop', [('HASH', "#112233")])),

    (DC('prop', "rgb(16, 32, 50.2%)"),
     ('prop', [('HASH', "#102080")])),

    (DC('prop', "rgba(-100%, 312.6%, 5, .5)"),
     ('prop', [('HASH', "#00FF0580")])),

    (DC('prop', "hsl(0, 50%, 50%)"),
     ('prop', [('HASH', "#BF4040")])),

    (DC('prop', "hsla(123.4, 250%, 13.54%, 0.1)"),
     ('prop', [('HASH', "#0045041A")])),
])
def test_translate_colors(decl, expected_decl):
    dumper.translate_colors(decl, '')
    assert (decl.name, list(jsonify(decl.value))) == expected_decl


@pytest.mark.parametrize(('decl', 'expected_error'), [
    (DC('prop', "#12345"),
     "unexpected length of 5 of color hash for property prop"),

    (DC('prop', "\"#12345\""),
     "unexpected length of 5 of color hash for property prop"),

    (DC('prop', "yolo()"),
     "unknown function 'yolo()' in property prop"),

    (DC('prop', "rgb()"),
     "expected 3 parameters for function 'rgb()', got 0"),

    (DC('prop', "rgb()"),
     "expected 3 parameters for function 'rgb()', got 0"),

    (DC('prop', "rgba(1, 2, 3, 4, 5)"),
     "expected 4 parameters for function 'rgba()', got 5"),

    (DC('prop', "rgb(1, 2 3, 4)"),
     "expected 1 token for parameter 2 in function 'rgb()', got 3"),

    (DC('prop', "rgb(1, 2, 3}"),
     "expected 1 token for parameter 3 in function 'rgb()', got 2"),

    # Can't test all possible value types here, so only cover all params and
    # possible values as a whole
    (DC('prop', "rgb(hi, 2, 3)"),
     "unexpected IDENT value for parameter 1 in function 'rgb()'"),

    (DC('prop', "rgb(1, 2, 2.2)"),
     "unexpected NUMBER value for parameter 3 in function 'rgb()'"),

    (DC('prop', "rgba(1, 2, 2, 10%)"),
     "unexpected PERCENTAGE value for parameter 4 in function 'rgba()'"),

    (DC('prop', "hsl(\"string\", 2%, 3%)"),
     "unexpected STRING value for parameter 1 in function 'hsl()'"),

    (DC('prop', "hsl(0, 2, 3%)"),
     "unexpected INTEGER value for parameter 2 in function 'hsl()'"),

    (DC('prop', "hsla(0, 2%, 3%, #123)"),
     "unexpected HASH value for parameter 4 in function 'hsla()'"),
])
def test_translate_colors_errors(decl, expected_error):
    try:
        dumper.translate_colors(decl, '')
        assert False, "no exception was raised"
    except DumpError as e:
        assert expected_error in str(e)
