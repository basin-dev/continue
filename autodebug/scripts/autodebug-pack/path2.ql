/**
 * @name Path
 * @description Path
 * @kind path-problem
 * @problem.severity recommendation
 * @id autodebug-pack/path
 */

import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs


// from DataFlow::CallCfgNode call, Function f, Parameter p
// where

// f.getLocation().getFile().getBaseName() = "test.py" and
//     f.getName() = "second" and
// p = f.getAnArg() and
    
// call = API::moduleImport("os").getMember("open").getACall()

// select call.getArg(0)

class MyConfiguration extends TaintTracking::Configuration {
    MyConfiguration() { this = "MyConfiguration" }
  
    override predicate isSource(DataFlow::Node source) {
      source.getLocation().getEndLine() = 13 and
      source.getLocation().getFile().getBaseName() = "test.py"
    }
  
    override predicate isSink(DataFlow::Node sink) {
      sink.getLocation().getEndLine() = 2 and
      sink.getLocation().getFile().getBaseName() = "importme.py"
    }
  }

from MyConfiguration dataflow, DataFlow::PathNode source, DataFlow::PathNode sink
where dataflow.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "."
