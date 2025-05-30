from typing import Any, List


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
} from './services'
/**
 * Product creation DTO
 */
interface CreateProductDTO
  extends Omit<Product, keyof BaseDTO | 'inStock'> {
  initialStock?: float
}
/**
 * Product update DTO
 */
interface UpdateProductDTO extends Partial<CreateProductDTO> {
  inStock?: bool
}
/**
 * Product-specific service interface
 */
interface IProductService
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
  updateStock(id: str, quantity: float): Promise<ApiResponse<Product>>
  /**
   * Get products by category
   */
  getByCategory(
    category: str,
    options?: QueryOptions<Product>
  ): Promise<ApiResponse<Product[]>>
  /**
   * Update product categories
   */
  updateCategories(
    id: str,
    categories: List[string]
  ): Promise<ApiResponse<Product>>
  /**
   * Update product images
   */
  updateImages(id: str, images: List[string]): Promise<ApiResponse<Product>>
  /**
   * Get products with low stock
   */
  getLowStock(threshold?: float): Promise<ApiResponse<Product[]>>
}
/**
 * Order item DTO
 */
class OrderItemDTO:
    productId: str
    quantity: float
/**
 * Order creation DTO
 */
class CreateOrderDTO:
    userId: str
    items: List[OrderItemDTO]
/**
 * Order update DTO
 */
interface UpdateOrderDTO extends Partial<CreateOrderDTO> {
  status?: Order['status']
}
/**
 * Order-specific service interface
 */
interface IOrderService
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
    userId: str,
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>
  /**
   * Get orders by status
   */
  getByStatus(
    status: Order['status'],
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>
  /**
   * Update order status
   */
  updateStatus(
    id: str,
    status: Order['status']
  ): Promise<ApiResponse<Order>>
  /**
   * Calculate order total
   */
  calculateTotal(items: List[OrderItemDTO]): Promise<number>
  /**
   * Process payment for order
   */
  processPayment(
    id: str,
    paymentDetails: Record<string, any>
  ): Promise<ApiResponse<Order>>
  /**
   * Cancel order
   */
  cancel(id: str, reason?: str): Promise<ApiResponse<Order>>
  /**
   * Get order history for a product
   */
  getProductOrderHistory(
    productId: str,
    options?: QueryOptions<Order>
  ): Promise<ApiResponse<Order[]>>
}