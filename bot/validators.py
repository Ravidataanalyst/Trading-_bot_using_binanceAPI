"""
Input Validation

Validates user input and order parameters with comprehensive error checking.
"""

import re
import logging
from typing import Dict, Any, List, Optional


class OrderValidator:
    """
    Validates order parameters and user input.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Valid order sides and types
        self.valid_sides = ['BUY', 'SELL']
        self.valid_order_types = ['MARKET', 'LIMIT']
        self.valid_time_in_force = ['GTC', 'IOC', 'FOK']
        
        # Symbol pattern (letters only, followed by USDT)
        self.symbol_pattern = re.compile(r'^[A-Z]+USDT$')
    
    def validate_order(self, symbol: str, side: str, order_type: str, 
                      quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Validate basic order parameters.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            order_type: Order type ('MARKET' or 'LIMIT')
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            
        Returns:
            Validation result with validity flag and error messages
        """
        errors = []
        
        # Validate symbol
        symbol_errors = self._validate_symbol(symbol)
        errors.extend(symbol_errors)
        
        # Validate side
        side_errors = self._validate_side(side)
        errors.extend(side_errors)
        
        # Validate order type
        type_errors = self._validate_order_type(order_type)
        errors.extend(type_errors)
        
        # Validate quantity
        quantity_errors = self._validate_quantity(quantity)
        errors.extend(quantity_errors)
        
        # Validate price (if provided)
        if price is not None or order_type == 'LIMIT':
            price_errors = self._validate_price(price, order_type)
            errors.extend(price_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_with_symbol_info(self, quantity: float, price: Optional[float], 
                                 order_type: str, symbol_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate order parameters against symbol information.
        
        Args:
            quantity: Order quantity
            price: Order price
            order_type: Order type
            symbol_info: Symbol information from exchange
            
        Returns:
            Validation result with validity flag and error messages
        """
        errors = []
        
        try:
            # Extract symbol filters
            filters = {f['filterType']: f for f in symbol_info.get('symbols', [{}])[0].get('filters', [])}
            
            # Validate quantity precision and limits
            if 'LOT_SIZE' in filters:
                lot_size = filters['LOT_SIZE']
                min_qty = float(lot_size['minQty'])
                max_qty = float(lot_size['maxQty'])
                step_size = float(lot_size['stepSize'])
                
                # Check minimum quantity
                if quantity < min_qty:
                    errors.append(f"Quantity {quantity} is below minimum {min_qty}")
                
                # Check maximum quantity
                if quantity > max_qty:
                    errors.append(f"Quantity {quantity} is above maximum {max_qty}")
                
                # Check quantity step precision
                if self._get_decimal_places(quantity) > self._get_decimal_places(step_size):
                    errors.append(f"Quantity precision too high. Max precision: {self._get_decimal_places(step_size)} decimal places")
            
            # Validate price precision and limits (for limit orders)
            if order_type == 'LIMIT' and price is not None:
                if 'PRICE_FILTER' in filters:
                    price_filter = filters['PRICE_FILTER']
                    min_price = float(price_filter['minPrice'])
                    max_price = float(price_filter['maxPrice'])
                    tick_size = float(price_filter['tickSize'])
                    
                    # Check minimum price
                    if price < min_price:
                        errors.append(f"Price {price} is below minimum {min_price}")
                    
                    # Check maximum price
                    if price > max_price:
                        errors.append(f"Price {price} is above maximum {max_price}")
                    
                    # Check price tick precision
                    if self._get_decimal_places(price) > self._get_decimal_places(tick_size):
                        errors.append(f"Price precision too high. Max precision: {self._get_decimal_places(tick_size)} decimal places")
            
            # Validate notional value (price * quantity)
            if 'MIN_NOTIONAL' in filters:
                min_notional = float(filters['MIN_NOTIONAL']['notional'])
                notional_value = quantity * (price if price is not None else 0)
                
                if order_type == 'LIMIT' and notional_value < min_notional:
                    errors.append(f"Notional value {notional_value} is below minimum {min_notional}")
            
        except (KeyError, ValueError, TypeError) as e:
            self.logger.warning(f"Could not validate with symbol info: {str(e)}")
            errors.append(f"Symbol info validation error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_symbol(self, symbol: str) -> List[str]:
        """Validate trading symbol."""
        errors = []
        
        if not symbol:
            errors.append("Symbol is required")
            return errors
        
        if not isinstance(symbol, str):
            errors.append("Symbol must be a string")
            return errors
        
        if not self.symbol_pattern.match(symbol):
            errors.append("Symbol must be in format like 'BTCUSDT' (letters followed by USDT)")
        
        return errors
    
    def _validate_side(self, side: str) -> List[str]:
        """Validate order side."""
        errors = []
        
        if not side:
            errors.append("Order side is required")
            return errors
        
        if not isinstance(side, str):
            errors.append("Order side must be a string")
            return errors
        
        if side.upper() not in self.valid_sides:
            errors.append(f"Order side must be one of: {', '.join(self.valid_sides)}")
        
        return errors
    
    def _validate_order_type(self, order_type: str) -> List[str]:
        """Validate order type."""
        errors = []
        
        if not order_type:
            errors.append("Order type is required")
            return errors
        
        if not isinstance(order_type, str):
            errors.append("Order type must be a string")
            return errors
        
        if order_type.upper() not in self.valid_order_types:
            errors.append(f"Order type must be one of: {', '.join(self.valid_order_types)}")
        
        return errors
    
    def _validate_quantity(self, quantity: float) -> List[str]:
        """Validate order quantity."""
        errors = []
        
        if quantity is None:
            errors.append("Quantity is required")
            return errors
        
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid number")
            return errors
        
        if quantity <= 0:
            errors.append("Quantity must be positive")
        
        return errors
    
    def _validate_price(self, price: Optional[float], order_type: str) -> List[str]:
        """Validate order price."""
        errors = []
        
        if order_type == 'LIMIT':
            if price is None:
                errors.append("Price is required for limit orders")
                return errors
            
            try:
                price = float(price)
            except (ValueError, TypeError):
                errors.append("Price must be a valid number")
                return errors
            
            if price <= 0:
                errors.append("Price must be positive")
        
        elif order_type == 'MARKET' and price is not None:
            errors.append("Price should not be provided for market orders")
        
        return errors
    
    def _get_decimal_places(self, number: float) -> int:
        """Get the number of decimal places in a number."""
        str_number = str(number)
        if '.' in str_number:
            return len(str_number.split('.')[1])
        return 0
    
    def validate_api_credentials(self, api_key: str, api_secret: str) -> Dict[str, Any]:
        """
        Validate API credentials format.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate API key
        if not api_key:
            errors.append("API key is required")
        elif not isinstance(api_key, str):
            errors.append("API key must be a string")
        elif len(api_key) < 10:
            errors.append("API key appears to be invalid (too short)")
        
        # Validate API secret
        if not api_secret:
            errors.append("API secret is required")
        elif not isinstance(api_secret, str):
            errors.append("API secret must be a string")
        elif len(api_secret) < 10:
            errors.append("API secret appears to be invalid (too short)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
