import { MigrationInterface, QueryRunner } from "typeorm";

export class CreateOrderTable1682470772393 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(
      `CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE,
                order_total NUMERIC,
                shipping_address TEXT,
                billing_address TEXT,
                payment_method TEXT,
                order_status TEXT,
                tracking_number TEXT
            )`
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP TABLE orders`);
  }
}
