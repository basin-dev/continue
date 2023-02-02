# AutoDebug CodeQL Pack

A CodeQL Pack is a collection of queries that depends on some libraries. The dependencies are defined in `qlpack.yml`, which acts much like a `package.json`. You can install the dependencies that are already defined with `codeql pack install`. If you want to install a new dependency, use `codeql pack add <repo>/<package_name>`.

To run these queries in development, you should

1. Download the CodeQL VSCode extension
2. Create a database using `codeql database create <path_where_db_will_be_created> --language=python --source-root=<folder_whose_code_you_want_to_analyze>`. To keep things consistent, it is recommended to use `scripts/testdb` and `scripts/db-files` as the db and source files.
3. Click the "QL" sidebar icon, then create a database from a folder and choose the one you just created.
4. Open the `.ql` file that you want to run, use `cmd+shift+p` to open the command palette, then do `CodeQL: Run Query`. The results will show up in an interactive window on the right.
