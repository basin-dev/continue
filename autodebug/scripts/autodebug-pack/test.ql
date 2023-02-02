/**
 * @name Test
 * @description Test
 * @kind problem
 * @problem.severity recommendation
 * @id autodebug-pack/test
 */

 import python

 from Function f, Stmt s
 where
 f.getLocation().getFile().getBaseName() = "test.py" and
    f.getName() = "second" and
 s = f.getAStmt() and
    s.getLocation().getEndLine() = 10
 select s, "..."