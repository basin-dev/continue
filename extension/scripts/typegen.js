const fs = require("fs");
const path = require("path");
const { compile } = require("json-schema-to-typescript");

function generateTypesForFile(schemaPath) {
  let schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  let name = (schemaPath.split("/").pop() || schemaPath).split(".")[0];
  // This is to solve the issue of json-schema-to-typescript not supporting $ref at the top-level, which is what Pydantic generates for recursive types
  if ("$ref" in schema) {
    let temp = schema["$ref"];
    delete schema["$ref"];
    schema["allOf"] = [{ $ref: temp }];
  }

  compile(schema, name).then((ts) => {
    fs.writeFileSync("schema/" + name + ".d.ts", ts);
  });
}

function generateAllSchemas(rootFolder) {
  try {
    fs.readdirSync(rootFolder).forEach((file) => {
      generateTypesForFile(path.join(rootFolder, file));
    });
  } catch (e) {
    console.log(
      "You are probably running this from a different directory, try running it from extensions/."
    );
    throw e;
  }
}

generateAllSchemas("../schema/");
