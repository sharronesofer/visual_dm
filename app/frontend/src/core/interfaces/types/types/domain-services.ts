import { Product, Order } from './models';
import { BaseDTO } from './common';
import {
  IBaseService,
  IPaginatedService,
  ISearchableService,
  IBulkService,
  ICacheableService,
  IRealtimeService,
  IValidatableService,
  IActionableService,
  IRelationalService,
  IVersionedService,
} from './services';
import { QueryOptions } from './query';
import { ApiResponse } from './common';

/**
 * Product creation DTO
 */
export interface CreateProductDTO
  extends Omit<Product, keyof BaseDTO | 'inStock'> {
  initialStock?: number;
}

/**
 * Product update DTO
 */
export interface UpdateProductDTO extends Partial<CreateProductDTO> {
  inStock?: boolean;
}

/**
 * Product-specific service interface
 */
export interface IProductService
  extends IBaseService<Product, CreateProductDTO, UpdateProductDTO>,
    IPaginatedService<Product, CreateProductDTO, UpdateProductDTO>,
    ISearchableService<Product, CreateProductDTO, UpdateProductDTO>,
    IBulkService<Product, CreateProductDTO, UpdateProductDTO>,
    ICacheableService<Product, CreateProductDTO, UpdateProductDTO>,
    IRealtimeService<Product, CreateProductDTO, UpdateProductDTO>,
    IValidatableService<Product, CreateProductDTO, UpdateProductDTO> {
  /**
   * Update product stock
   */
  updateStock(id: string, quantity: number): Promise<ApiResponse<Product>>;

  /**
   * Get products by category
   */
  getByCategory(
    category: string,
    options?: QueryOptions<Product>
  ): Promise<ApiResponse<Product[]>>;

  /**
   * Update product categories
   */
  updateCategories(
    id: string,
    categories: string[]
  ): Promise<ApiResponse<Product>>;

  /**
   * Update product images
   */
  updateImages(id: string, images: string[]): Promise<ApiResponse<Product>>;

  /**
   * Get products with low stock
   */
  getLowStock(threshold?: number): Promise<ApiResponse<Product[]>>;
}

/**
 * Order item DTO
 */
export interface OrderItemDTO {
  productId: string;
  quantity: number;
}

/**
 * Order creation DTO
 */
export interface CreateOrderDTO {
  userId: string;
  items: OrderItemDTO[];
}

/**
 * Order update DTO
 */
export interface UpdateOrderDTO extends Partial<CreateOrderDTO> {
  status?: Order['status'];
}

/**
 * Order-specific service interface
 */
export interface IOrderService
  extends IBaseService<Order, CreateOrderDTO, UpdateOrderDTO>,
    IPaginatedService<Order, CreateOrderDTO, UpdateOrderDTO>,
    ISearchableService<Order, CreateOrderDTO, UpdateOrderDTO>,
    ICacheableService<Order, CreateOrderDTO, UpdateOrderDTO>,
    IRealtimeService<Order, CreateOrderDTO, UpdateOrderDTO>,
    IValidatableService<Order, CreateOrderDTO, UpdateOrderDTO> {
  /**
   * Get orders by user
   */
  getByUser(
    userId: string,
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>;

  /**
   * Get orders by status
   */
  getByStatus(
    status: Order['status'],
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>;

  /**
   * Update order status
   */
  updateStatus(
    id: string,
    status: Order['status']
  ): Promise<ApiResponse<Order>>;

  /**
   * Calculate order total
   */
  calculateTotal(items: OrderItemDTO[]): Promise<number>;

  /**
   * Process payment for order
   */
  processPayment(
    id: string,
    paymentDetails: Record<string, any>
  ): Promise<ApiResponse<Order>>;

  /**
   * Cancel order
   */
  cancel(id: string, reason?: string): Promise<ApiResponse<Order>>;

  /**
   * Get order history for a product
   */
  getProductOrderHistory(
    productId: string,
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>;
}
