# `Airbyte` Plugin

1. Check out a new branch (what if changes?)
2. Make all tests and connectors available to model
3. Check for bypasses in the tests
4. Remove every bypass discovered
5. Run every test and see what connector columns it fails on
6. Have model determine what type each failing connector column should be
7. Repeats this for all columns across all connectors
8. Update tests to make sure they now pass
9. Open a pull request with the changes
10. Human reviews, fixes, and merges new code into main branch

Thoughts
- Is this a one off thing? would you really write a plugin for this?
- Is this something that someone could pick up and tweak for their similar situation?
- Or maybe this plugin is a composed out of a bunch of smaller steps?