# SDK

The `SDK` gives you access to tools (e.g. open a directory, edit a file, call an LLM, etc), which you can use when defining how a step should work and composing them with other steps.

## SDK methods

**Q: are we planning to make models.main, filesystem, filesystem_edit, etc. part of the SDK?** should not import anything but steps they have to import, nate make part of SDK

### run_step

### edit_file

Edits a file

#### Parameters

- `filepath` (required): the location of the file that should be edited
- `prompt` (required): instructions for how the LLM should edit the file

**Q: what if you want to pass context of previous steps, other files, etc?** observations before, some sort of memory, whole new concept?

### run

Runs a command

#### Parameters

- `command` (required): the command that should be run

**Q: how do we adjust the commands for different operating systems?** likely handled within steps

### wait_for_user_confirmation

Waits for the user to review the steps that ran before running the next steps

#### Paramaters

- `question` (required): asks the user to confirm something specific

### ide.getOpenFiles

Gets the name of the files that are open in the IDE currently

### sdk.ide.readFile

Gets the contents of the file located at the `filepath` 

#### Paramaters

- `filepath` (required): the location of the file that should be read

### sdk.ide.get_recent_edits

**Q: what does this method do?**