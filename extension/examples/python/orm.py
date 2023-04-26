import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Create the engine
engine = create_engine('sqlite:///:memory:', echo=True)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create a base class
Base = declarative_base()

# Create the tables


class User(Base):
    """
    Continue: depends[
        sqlalchemy,
        sqlalchemy.orm,
        sqlalchemy.ext.declarative,
        "sql file?"
    ]
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    # Create a relationship
    addresses = relationship("Address", back_populates="user")

    # Create a string representation
    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)


# What are things that might need to be marked for update?
"""
Can automatically mark (but these are things that already automatically show up in Problems tab of IDE):
- Subclasses for implementation of abstract method
- Calls of edited function
- New function -> Test
- Change to interface changes everywhere where it is implemented (example is React props)
- Switch statements that aren't completely exhaustive (but this is just an LSP thing, and a type-checker thing in good languages like TS)

Non-automatic:
- Chromium sync/async lists
- ORM updates
- Protocols: Edit one side, must edit the other
- "This function/class/file 'watches' these other functions/classes/files, and if they are updated, it should be patched"
- Depends on outside documentation (give it a URL, or a PyPI package or something, github repo/path)
- Depends on database schema: can you write a script to determine if dependency changed, or a command to run, or we can have some builtin dependency checkers? Postgres might be common. Dependabot is an example of this concept.
- Breaking changes to packages (for example, it could keep my iOS apps up-to-date without me doing work) Wonder what kind of time people spend on this.
- W3C specs or other standards updated


Other ways to detect:
- These two files/functions/classes are usually committed together
- In general, when a file is changed, run through the whole thing and see if any missed changes

Smaller examples:
- Write using variables that aren't defined yet, have them defined

Hybrid code generation:
Make it really easy for developers to write code generators.
Don't worry about writing the boilerplate, because GPT can get it right most of the time.
Makes it really easy to generate code, and much code is generated at many companies.
The benefit is when no code is generated?

Any examples in your codebase?
- Switch statements in handleMessage
- Protocol in debugPanel.ts and littered across react app (want to be able to write a docstring inside requestVsc() function that says "everytime I am called in a new place with a new argument, you need to add to the switch statement")
- Update readme whenever a new npm script is added
- Update documentation whenever somethign is changed/added
- telemetry.ts: add new event, place the call in the file where it belongs, or raise that human needs to do this. Or, if new enum statement added (can be done by refactor), then add the comment
- In bridge.ts, you were adding a function for every API endpoint
- In snoopers.ts, for each of the keys (static vars need to have switch statement
- DEFAULT_SNOOPERS in terminalEmulator.ts
- getDefaultShell in terminalEmulator.ts could depend on OS details
- Super useful in src/languages, where you had to implement function in each language, OR mark as not implemented, but for some reason you didn't want to use a class
- Calling environmentSetup.ts scripts, what if the path to the files changes?
- Check for missing dependencies in React useEffect/useCallback
- REDUX: First change interface, then slice, then selector. Can we let companies make their own custom refactor actions in VS Code?
- If any API params were changed on OAI API
- MODELS_TO_GENERATE in gen_json_schema.py

"""

"""
Think about the protocol example: How do you want to define it?

In python, want to write something like the below, and typescript like this:

class Protocol {
    // Continue: depends["protocol.py"::protocol_message_types]
    // Continue: prompt[
    //     "Implement function for each message type"
    // ]

    def handleType1() {
        pass
    }

    def handleMessage(message) {
        // Continue: depends["protocol.py"::protocol_message_types]
        // Continue: prompt[
        //     "Write a switch statement for each message type that calls the appropriate function"
        // ]
        switch (message) {
            case "type1":
                break;
        }
    }
}
"""

"""
git log -L :myfunction:path/to/myfile.c will show you changes to a function in a git diff.
Could probably do this for variables/classes/files too. This works if just a CI tool.
Otherwise, see if language server can help. Position of edit -> LSP?
"""

"""
Different descriptions of what we're doing:
Avoid technical debt
Bot code ownership
Hybrid code generation
CI/CD layer between compiler and reviewer
"""

"""
Complete other thing:
- Probably hard to enforce code standards for small companies
Maybe they use ESLint, but prob doesn't cover everything
They don't have time to write custom parsers
So we could make it easier to enforce practices in PR

- Linked embedding search
"""


"""
General concerns:
- If what you're doing should be a public good, then be careful
- Next models probably plateauing, doing completely different things
If plateuing, then will be slower and more powerful.
So want to look at async tasks. PR review is great example.
- Plugins shwo that we didn't learn the end-to-end lesson
- When does this only promote bad programming style?
- What about false negatives in patching?
"""

protocol_message_types = [
    "type1"
]


class Protocol:
    """Continue: depends[protocol_message_types]
    Continue: prompt[
        Implement function for each message type
    ]
    """

    def handle_message(self, message):
        """Continue: depends[protocol_message_types]
        Continue: prompt[
            Write a switch statement for each message type that calls the appropriate function
        ]
        """
        if message == "type1":
            self.handleType1()
        else:
            pass

    def handleType1(self):
        pass
