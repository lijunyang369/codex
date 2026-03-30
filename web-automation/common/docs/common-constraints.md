# Common Constraints

## Encoding Safety

For Chinese text input on browser automation tasks:

1. Do not write Chinese text through an unverified text injection path.
2. Prefer UTF-8 safe transport, such as base64 + in-page UTF-8 decode, when going through PowerShell / Node / CDP chains.
3. After every write, immediately verify page text by reading it back from the target page.
4. Do not continue to the next field until the current field is confirmed correct.
5. If page text shows `？` or `????`, treat it as a write failure and repair it before any further edits.

## Boss-Specific Rule

For BOSS直聘:

- Standardized fields such as position, industry, and certification should prefer component-state updates over raw DOM input.
- If the UI flow is unstable, prefer the component save path or parent save path.
