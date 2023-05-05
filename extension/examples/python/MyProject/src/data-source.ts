import { Entity, PrimaryGeneratedColumn, Column } from "typeorm";

@Entity()
export class Order {
  @PrimaryGeneratedColumn()
  order_id: number;

  @Column({ nullable: true })
  customer_id: number;

  @Column({ nullable: true })
  order_date: Date;

  @Column({ nullable: true })
  order_total: number;

  @Column({ nullable: true })
  shipping_address: string;

  @Column({ nullable: true })
  billing_address: string;

  @Column({ nullable: true })
  payment_method: string;

  @Column({ nullable: true })
  order_status: string;

  @Column({ nullable: true })
  tracking_number: string;
}
