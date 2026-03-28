"""
Order Placement Logic

Handles order creation, validation, and execution with proper error handling
and response formatting.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from .client import BinanceFuturesClient
from .validators import OrderValidator


class OrderManager:
    """
    Manages order placement and tracking for Binance Futures Testnet.
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize the order manager.
        
        Args:
            client: Binance Futures client instance
        """
        self.client = client
        self.validator = OrderValidator()
        self.logger = logging.getLogger(__name__)
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order with validation and error handling.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            order_type: Order type ('MARKET' or 'LIMIT')
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            
        Returns:
            Formatted order response with success/failure information
        """
        try:
            # Log order request
            self.logger.info(f"Placing order: {side} {quantity} {symbol} @ {order_type}")
            if price:
                self.logger.info(f"Order price: {price}")
            
            # Validate order parameters
            validation_result = self.validator.validate_order(
                symbol, side, order_type, quantity, price
            )
            
            if not validation_result['valid']:
                error_msg = f"Order validation failed: {validation_result['errors']}"
                self.logger.error(error_msg)
                return self._format_error_response(error_msg, validation_result['errors'])
            
            # Get symbol info for additional validation
            try:
                symbol_info = self.client.get_symbol_info(symbol)
                self.logger.debug(f"Symbol info retrieved for {symbol}")
            except Exception as e:
                self.logger.warning(f"Could not retrieve symbol info for {symbol}: {str(e)}")
                symbol_info = None
            
            # Additional validation with symbol info
            if symbol_info:
                symbol_validation = self.validator.validate_with_symbol_info(
                    quantity, price, order_type, symbol_info
                )
                if not symbol_validation['valid']:
                    error_msg = f"Symbol validation failed: {symbol_validation['errors']}"
                    self.logger.error(error_msg)
                    return self._format_error_response(error_msg, symbol_validation['errors'])
            
            # Place the order
            order_response = self.client.place_order(symbol, side, order_type, quantity, price)
            
            # Log successful order
            self.logger.info(f"Order placed successfully. Order ID: {order_response.get('orderId')}")
            
            # Format and return response
            return self._format_success_response(order_response, symbol, side, order_type, quantity, price)
            
        except Exception as e:
            error_msg = f"Failed to place order: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._format_error_response(error_msg, [str(e)])
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get the status of an existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Formatted order status response
        """
        try:
            self.logger.info(f"Getting order status for {symbol} order {order_id}")
            
            order_status = self.client.get_order_status(symbol, order_id)
            
            self.logger.info(f"Order status retrieved: {order_status.get('status')}")
            
            return {
                'success': True,
                'order_id': order_status.get('orderId'),
                'symbol': order_status.get('symbol'),
                'status': order_status.get('status'),
                'side': order_status.get('side'),
                'type': order_status.get('type'),
                'quantity': order_status.get('origQty'),
                'executed_quantity': order_status.get('executedQty'),
                'price': order_status.get('price'),
                'avg_price': order_status.get('avgPrice'),
                'update_time': order_status.get('updateTime'),
                'message': 'Order status retrieved successfully'
            }
            
        except Exception as e:
            error_msg = f"Failed to get order status: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Failed to retrieve order status'
            }
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Formatted cancellation response
        """
        try:
            self.logger.info(f"Cancelling order {order_id} for {symbol}")
            
            cancel_response = self.client.cancel_order(symbol, order_id)
            
            self.logger.info(f"Order cancelled successfully. Order ID: {cancel_response.get('orderId')}")
            
            return {
                'success': True,
                'order_id': cancel_response.get('orderId'),
                'symbol': cancel_response.get('symbol'),
                'status': cancel_response.get('status'),
                'message': 'Order cancelled successfully'
            }
            
        except Exception as e:
            error_msg = f"Failed to cancel order: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Failed to cancel order'
            }
    
    def _format_success_response(self, order_response: Dict[str, Any], symbol: str, 
                               side: str, order_type: str, quantity: float, 
                               price: Optional[float]) -> Dict[str, Any]:
        """
        Format a successful order response.
        
        Args:
            order_response: Raw API response
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price
            
        Returns:
            Formatted success response
        """
        return {
            'success': True,
            'order_id': order_response.get('orderId'),
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity),
            'price': str(price) if price else None,
            'status': order_response.get('status'),
            'executed_quantity': order_response.get('executedQty'),
            'avg_price': order_response.get('avgPrice'),
            'transact_time': order_response.get('transactTime'),
            'client_order_id': order_response.get('clientOrderId'),
            'fills': order_response.get('fills', []),
            'message': 'Order placed successfully'
        }
    
    def _format_error_response(self, error_msg: str, errors: list) -> Dict[str, Any]:
        """
        Format an error response.
        
        Args:
            error_msg: Main error message
            errors: List of specific errors
            
        Returns:
            Formatted error response
        """
        return {
            'success': False,
            'error': error_msg,
            'validation_errors': errors,
            'message': 'Order placement failed'
        }
