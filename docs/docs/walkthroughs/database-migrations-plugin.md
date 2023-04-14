- need to create migration file
- create a database table
- add model for ORM
- very tedious
- have one easily generate
- Frameworks automate with boilerplate
- Make you fill in things
- People will edit migration but forget model file
- Format you need to follow
- Can’t solve the business logic
- Create a migration file that adds a column
- tested with chatgpt
- able to generate an interface / object
- Right now using TypeScript, using TypeORM, using NestJS backend framework

based on 
- https://www.tutorialspoint.com/typeorm/typeorm_migrations.htm
- https://github.com/typeorm/typeorm/blob/master/docs/migrations.md

0. Slash command for TypeORM migration with some natural language input about the migration (required value?)
1. Check if the connection in `ormconfig.json` has been set up. If not, ask user to do it with instructions on how to do it
2. Once it is, automatically fill in the new / adjusted entity (based on info provided) and wait for approval from developer
3. Execute CLI command to create a new migration
4. Look for migration response
5. Add up / down methods to add / revert changes in the migration and ask for review from developer
6. Make sure output of migrations looks good

while not CheckTypeORMConnectionStep():
  WaitForUserStep()
EditTypeORMEntityStep()
WaitForUserStep()
while not TypeORMCLICommandStep():
  WaitForUserStep()
EditTypeORMMethodsStep()
CheckMigrationsStep()

Side effects on the database??
Too structured already??