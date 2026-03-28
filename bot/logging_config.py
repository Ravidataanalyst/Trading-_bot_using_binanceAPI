"""
Logging Configuration

Sets up structured logging for the trading bot with file and console output.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class TradingBotLogger:
    """
    Configures and manages logging for the trading bot.
    """
    
    def __init__(self, log_level: str = 'INFO', log_dir: str = 'logs'):
        """
        Initialize the logger configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = log_dir
        self.log_file = None
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f'trading_bot_{timestamp}.log')
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up the logging configuration."""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Console shows INFO and above
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Log the setup
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized - Level: {logging.getLevelName(self.log_level)}")
        logger.info(f"Log file: {self.log_file}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def log_api_request(logger: logging.Logger, method: str, endpoint: str, 
                       params: Optional[dict] = None):
        """
        Log API request details.
        
        Args:
            logger: Logger instance
            method: HTTP method
            endpoint: API endpoint
            params: Request parameters
        """
        logger.info(f"API Request: {method} {endpoint}")
        if params:
            # Sanitize sensitive data
            sanitized_params = params.copy()
            for key in ['signature', 'api_key', 'api_secret']:
                if key in sanitized_params:
                    sanitized_params[key] = '***REDACTED***'
            logger.debug(f"Request parameters: {sanitized_params}")
    
    @staticmethod
    def log_api_response(logger: logging.Logger, status_code: int, 
                        response_data: Optional[dict] = None):
        """
        Log API response details.
        
        Args:
            logger: Logger instance
            status_code: HTTP status code
            response_data: Response data
        """
        logger.info(f"API Response: Status {status_code}")
        if response_data:
            # Log key response fields
            key_fields = {}
            if 'orderId' in response_data:
                key_fields['orderId'] = response_data['orderId']
            if 'status' in response_data:
                key_fields['status'] = response_data['status']
            if 'symbol' in response_data:
                key_fields['symbol'] = response_data['symbol']
            
            logger.debug(f"Response data: {response_data}")
            if key_fields:
                logger.info(f"Key response fields: {key_fields}")
    
    @staticmethod
    def log_order_request(logger: logging.Logger, symbol: str, side: str, 
                         order_type: str, quantity: float, price: Optional[float] = None):
        """
        Log order request details.
        
        Args:
            logger: Logger instance
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price
        """
        logger.info(f"Order Request - Symbol: {symbol}, Side: {side}, Type: {order_type}, Quantity: {quantity}")
        if price is not None:
            logger.info(f"Order Request - Price: {price}")
    
    @staticmethod
    def log_order_response(logger: logging.Logger, order_response: dict):
        """
        Log order response details.
        
        Args:
            logger: Logger instance
            order_response: Order response from API
        """
        if order_response.get('success', False):
            logger.info(f"Order Success - ID: {order_response.get('order_id')}, Status: {order_response.get('status')}")
            logger.info(f"Order Details - Symbol: {order_response.get('symbol')}, Side: {order_response.get('side')}")
            logger.info(f"Order Details - Type: {order_response.get('type')}, Quantity: {order_response.get('quantity')}")
            
            # Log execution details if available
            executed_qty = order_response.get('executed_quantity')
            avg_price = order_response.get('avg_price')
            if executed_qty and avg_price:
                logger.info(f"Execution - Executed Qty: {executed_qty}, Avg Price: {avg_price}")
        else:
            logger.error(f"Order Failed - Error: {order_response.get('error')}")
            if order_response.get('validation_errors'):
                logger.error(f"Validation Errors: {order_response['validation_errors']}")
    
    @staticmethod
    def log_error(logger: logging.Logger, error: Exception, context: str = ""):
        """
        Log error with context.
        
        Args:
            logger: Logger instance
            error: Exception that occurred
            context: Additional context information
        """
        if context:
            logger.error(f"Error in {context}: {str(error)}", exc_info=True)
        else:
            logger.error(f"Error: {str(error)}", exc_info=True)


def setup_logging(log_level: str = 'INFO', log_dir: str = 'logs') -> TradingBotLogger:
    """
    Set up logging for the trading bot.
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
        
    Returns:
        TradingBotLogger instance
    """
    return TradingBotLogger(log_level, log_dir)
