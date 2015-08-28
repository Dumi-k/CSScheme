CSScheme Changelog
==================

v1.2.0 (2015-08-28)
-------------------

- You can create `.hidden-tmTheme` files by adding a global `@hidden: true;`
  rule to the source. The rule is consumed and the output file's extension
  adjusted. (#9)
- The global `@name` rule is now optional. Sublime Text doesn't use it anyway.
- The built example schemes are now hidden, so they don't pop up in the
  "Prefereces > Color Scheme" menu anymore


v1.1.1 (2015-03-17)
-------------------

- 'shadowWidth' is now a known property (as integer) and its value is checked
- Literal integers are now supported, such as `shadowWidth: 10;`
- Completions have received an additional tab trigger to skip the semi colon


v1.1.0 (2015-02-14)
-------------------

- ST2 support has been removed! Old releases are still available but
  development will continue only for ST3.
- Added command to convert from tmTheme to CSScheme ("CSScheme: Convert to
  CSScheme") (#8)
- Changed hyphen escape sequence for SASS/SCSS from `'-'` to `\-`, which works
  with the current SASS parser (#7)
- Fixed a bug where uuids with leading zeros were not recognized


v1.0.0 (2014-08-28)
-------------------

- The settings management for executable paths has been changed!
  If you depend on this, you'll have to revisit.
- Added support for stylus! (an example file has been bundled as well)

- If running a pre-compiler, the compiled result will always be shown if there
  was an error parsing it
- Added commands to create a new csscheme file (or variation) based on templates
- Added command palette entries to open the readme and settings files
- DumpErrors now show the same debug output as ParseErrors
- Fixed long relative path references in some situations (mainly stylus)
- Fixed wrong syntax file reference with `"preview_compiled_css": true`
- SASScheme files now also get a dedicated syntax which allows CSScheme to more
  accurately match its build system (same for stylus). This relies on the
  external "Sass" package.
- Fixed wrong line number being displayed when an at-rule was encountered
  multiple times
- Added punctuation scopes to auto completion (csscheme, scsscheme)


v0.3.0 (2014-03-08)
-------------------

- Differentiate between style and options list ("fontStyle" vs e.g.
  "tagsOptions") for validation (also #2)
- Allow `"fontStyle": none;` for empty style list (#4)
- Highlight SASS's `index` function
- Fix not showing error message if a line number was not found from the
  compiled SCSS (within the last x lines)
- Added snippets for `@for`, `@each`, `@else if`, `@else`, `@while`
- All "package" related files were moved to a sub-directory


v0.2.1 (2014-03-01)
-------------------

- Added "foreground" to allowed style list properties (.g. "bracketsOptions")


v0.2.0 (2014-02-24)
-------------------

- Added more known_properties to check values against (#2)
- Fixed errors when using functions in "unknown" properties (#1)
- Fixed incorrect error messages for empty output from running `sass`
- Fixed unexpected behavior from running `sass` on non-Windows


v0.1.1 (2014-02-24)
-------------------

- Removed `$` form the SCSS word separator list


v0.1.0 (2014-02-22)
-------------------

- Initial release
