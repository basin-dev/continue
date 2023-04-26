import "reflect-metadata";
import { DataSource } from "typeorm";
import { User } from "./entity/User";
import { Order } from "./entity/Order";

export const AppDataSource = new DataSource({
  type: "sqlite",
  database: "database.sqlite",
  synchronize: true,
  logging: false,
  entities: [User, Order],
  migrations: [],
  subscribers: [],
});
