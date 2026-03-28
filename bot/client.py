"""
Binance Futures Testnet Client Wrapper

A wrapper around the Binance Futures Testnet API that handles authentication,
requests, and responses with proper error handling and logging.
"""

import os
import time
import hashlib
import hmac
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode


class BinanceFuturesClient:
    """
    Client for interacting with Binance Futures Testnet API.
    
    Handles authentication, request signing, and API calls with proper error handling.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://testnet.binancefuture.com"):
        """
        Initialize the Binance Futures client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            base_url: Base URL for the testnet API
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-MBX-APIKEY': api_key
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC-SHA256 signature for API requests.
        
        Args:
            params: Query parameters to sign
            
        Returns:
            Hex-encoded signature string
        """
        # Create query string
        query_string = urlencode(params)
        
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                      signed: bool = False) -> Dict[str, Any]:
        """
        Make an HTTP request to the Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether the request needs to be signed
            
        Returns:
            JSON response from the API
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        # Add timestamp for signed requests
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            
            # Generate signature
            signature = self._generate_signature(params)
            params['signature'] = signature
        
        # Log request details
        self.logger.info(f"Making {method} request to {endpoint}")
        self.logger.debug(f"Parameters: {params}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, data=params)
            elif method == 'DELETE':
                response = self.session.delete(url, data=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Log response details
            self.logger.info(f"Response status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                self.logger.debug(f"Response data: {data}")
                return data
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('msg', f'HTTP {response.status_code}: {response.text}')
                self.logger.error(f"API request failed: {error_msg}")
                raise Exception(f"Binance API Error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except ValueError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information including balances.
        
        Returns:
            Account information dictionary
        """
        return self._make_request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get exchange information for a specific symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Symbol information dictionary
        """
        params = {'symbol': symbol}
        return self._make_request('GET', '/fapi/v1/exchangeInfo', params)
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None, 
                   time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a futures order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            order_type: Order type ('MARKET' or 'LIMIT')
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response dictionary
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity)
        }
        
        # Add price for limit orders
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for limit orders")
            params['price'] = str(price)
            params['timeInForce'] = time_in_force
        
        return self._make_request('POST', '/fapi/v1/order', params, signed=True)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('GET', '/fapi/v1/order', params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Cancellation response dictionary
        """
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/fapi/v1/order', params, signed=True)
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("Binance client session closed")
