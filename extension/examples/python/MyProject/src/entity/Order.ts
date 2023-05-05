import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class Order {
  @PrimaryGeneratedColumn()
  order_id: number;

  @Column()
  customer_id: number;

  @Column()
  order_date: Date;

  @Column()
  order_total: number;

  @Column()
  shipping_address: string;

  @Column()
  billing_address: string;

  @Column()
  payment_method: string;

  @Column()
  order_status: string;

  @Column()
  tracking_number: string;
}