CSScheme Changelog
==================

~current iteration~
-------------------

- Differentiate between style and options list ("fontStyle" vs e.g.
  "tagsOptions") for validation (also #2)
- Allow `"fontStyle": none;` for empty style list (#4)
- Highlight SASS's `index` function


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