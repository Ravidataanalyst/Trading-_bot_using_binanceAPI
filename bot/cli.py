"""
Command Line Interface

CLI entry point for the trading bot using argparse for user input handling.
"""

import argparse
import os
import sys
from typing import Optional
from .client import BinanceFuturesClient
from .orders import OrderManager
from .validators import OrderValidator
from .logging_config import setup_logging, TradingBotLogger


class TradingBotCLI:
    """
    Command line interface for the trading bot.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.logger = None
        self.client = None
        self.order_manager = None
        self.validator = OrderValidator()
    
    def setup_environment(self, log_level: str = 'INFO'):
        """
        Set up the environment including logging and API client.
        
        Args:
            log_level: Logging level
        """
        # Setup logging
        trading_logger = setup_logging(log_level)
        self.logger = trading_logger.get_logger(__name__)
        
        # Get API credentials from environment variables
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        if not api_key or not api_secret:
            self.logger.error("API credentials not found in environment variables")
            print("Error: Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
            sys.exit(1)
        
        # Validate API credentials
        validation_result = self.validator.validate_api_credentials(api_key, api_secret)
        if not validation_result['valid']:
            self.logger.error(f"Invalid API credentials: {validation_result['errors']}")
            print(f"Error: Invalid API credentials - {', '.join(validation_result['errors'])}")
            sys.exit(1)
        
        # Initialize client and order manager
        self.client = BinanceFuturesClient(api_key, api_secret)
        self.order_manager = OrderManager(self.client)
        
        self.logger.info("Trading bot environment initialized successfully")
    
    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser for CLI commands.
        
        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description='Binance Futures Testnet Trading Bot',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Place a market buy order
  python cli.py order BTCUSDT BUY MARKET 0.001
  
  # Place a limit sell order
  python cli.py order BTCUSDT SELL LIMIT 0.001 65000.00
  
  # Get order status
  python cli.py status BTCUSDT 123456789
  
  # Cancel an order
  python cli.py cancel BTCUSDT 123456789
  
  # Get account information
  python cli.py account
            """
        )
        
        # Add global options
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set the logging level (default: INFO)'
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Order command
        order_parser = subparsers.add_parser('order', help='Place a new order')
        order_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
        order_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
        order_parser.add_argument('type', choices=['MARKET', 'LIMIT'], help='Order type')
        order_parser.add_argument('quantity', type=float, help='Order quantity')
        order_parser.add_argument('price', nargs='?', type=float, help='Order price (required for LIMIT orders)')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Get order status')
        status_parser.add_argument('symbol', help='Trading symbol')
        status_parser.add_argument('order_id', type=int, help='Order ID')
        
        # Cancel command
        cancel_parser = subparsers.add_parser('cancel', help='Cancel an order')
        cancel_parser.add_argument('symbol', help='Trading symbol')
        cancel_parser.add_argument('order_id', type=int, help='Order ID')
        
        # Account command
        account_parser = subparsers.add_parser('account', help='Get account information')
        
        return parser
    
    def print_order_summary(self, symbol: str, side: str, order_type: str, 
                          quantity: float, price: Optional[float] = None):
        """
        Print order request summary.
        
        Args:
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price
        """
        print("\n" + "="*50)
        print("ORDER REQUEST SUMMARY")
        print("="*50)
        print(f"Symbol:     {symbol}")
        print(f"Side:       {side}")
        print(f"Type:       {order_type}")
        print(f"Quantity:   {quantity}")
        if price is not None:
            print(f"Price:      {price}")
        print("="*50)
    
    def print_order_response(self, response: dict):
        """
        Print order response details.
        
        Args:
            response: Order response dictionary
        """
        print("\n" + "="*50)
        print("ORDER RESPONSE")
        print("="*50)
        
        if response.get('success', False):
            print(f"Status:     SUCCESS")
            print(f"Order ID:   {response.get('order_id')}")
            print(f"Symbol:     {response.get('symbol')}")
            print(f"Side:       {response.get('side')}")
            print(f"Type:       {response.get('type')}")
            print(f"Quantity:   {response.get('quantity')}")
            if response.get('price'):
                print(f"Price:      {response.get('price')}")
            print(f"Status:     {response.get('status')}")
            
            # Print execution details if available
            executed_qty = response.get('executed_quantity')
            avg_price = response.get('avg_price')
            if executed_qty and executed_qty != '0':
                print(f"Executed:   {executed_qty}")
                if avg_price and avg_price != '0':
                    print(f"Avg Price:  {avg_price}")
            
            print(f"Message:    {response.get('message')}")
        else:
            print(f"Status:     FAILED")
            print(f"Error:      {response.get('error')}")
            if response.get('validation_errors'):
                print("Validation Errors:")
                for error in response['validation_errors']:
                    print(f"  - {error}")
        
        print("="*50)
    
    def print_account_info(self, account_info: dict):
        """
        Print account information.
        
        Args:
            account_info: Account information dictionary
        """
        print("\n" + "="*50)
        print("ACCOUNT INFORMATION")
        print("="*50)
        print(f"Total Wallet Balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
        print(f"Available Balance:    {account_info.get('availableBalance', 'N/A')} USDT")
        print(f"Total Unrealized PNL: {account_info.get('totalUnrealizedProfit', 'N/A')} USDT")
        print(f"Total Margin Balance: {account_info.get('totalMarginBalance', 'N/A')} USDT")
        
        # Print asset balances
        assets = account_info.get('assets', [])
        if assets:
            print("\nAsset Balances:")
            for asset in assets[:10]:  # Show first 10 assets
                asset_name = asset.get('asset')
                wallet_balance = asset.get('walletBalance')
                available_balance = asset.get('availableBalance')
                if float(wallet_balance) > 0:
                    print(f"  {asset_name}: {wallet_balance} (Available: {available_balance})")
        
        print("="*50)
    
    def handle_order_command(self, args):
        """
        Handle the order command.
        
        Args:
            args: Parsed command line arguments
        """
        # Print order summary
        self.print_order_summary(args.symbol, args.side, args.type, args.quantity, args.price)
        
        # Log order request
        TradingBotLogger.log_order_request(
            self.logger, args.symbol, args.side, args.type, args.quantity, args.price
        )
        
        # Place the order
        response = self.order_manager.place_order(
            args.symbol, args.side, args.type, args.quantity, args.price
        )
        
        # Log and print response
        TradingBotLogger.log_order_response(self.logger, response)
        self.print_order_response(response)
    
    def handle_status_command(self, args):
        """
        Handle the status command.
        
        Args:
            args: Parsed command line arguments
        """
        self.logger.info(f"Getting order status for {args.symbol} order {args.order_id}")
        
        response = self.order_manager.get_order_status(args.symbol, args.order_id)
        
        print("\n" + "="*50)
        print("ORDER STATUS")
        print("="*50)
        
        if response.get('success', False):
            print(f"Order ID:     {response.get('order_id')}")
            print(f"Symbol:       {response.get('symbol')}")
            print(f"Status:       {response.get('status')}")
            print(f"Side:         {response.get('side')}")
            print(f"Type:         {response.get('type')}")
            print(f"Quantity:     {response.get('quantity')}")
            print(f"Executed:     {response.get('executed_quantity')}")
            if response.get('avg_price'):
                print(f"Avg Price:    {response.get('avg_price')}")
            print(f"Update Time:  {response.get('update_time')}")
            print(f"Message:      {response.get('message')}")
        else:
            print(f"Status:       FAILED")
            print(f"Error:        {response.get('error')}")
            print(f"Message:      {response.get('message')}")
        
        print("="*50)
    
    def handle_cancel_command(self, args):
        """
        Handle the cancel command.
        
        Args:
            args: Parsed command line arguments
        """
        self.logger.info(f"Cancelling order {args.order_id} for {args.symbol}")
        
        response = self.order_manager.cancel_order(args.symbol, args.order_id)
        
        print("\n" + "="*50)
        print("ORDER CANCELLATION")
        print("="*50)
        
        if response.get('success', False):
            print(f"Status:       SUCCESS")
            print(f"Order ID:     {response.get('order_id')}")
            print(f"Symbol:       {response.get('symbol')}")
            print(f"Status:       {response.get('status')}")
            print(f"Message:      {response.get('message')}")
        else:
            print(f"Status:       FAILED")
            print(f"Error:        {response.get('error')}")
            print(f"Message:      {response.get('message')}")
        
        print("="*50)
    
    def handle_account_command(self, args):
        """
        Handle the account command.
        
        Args:
            args: Parsed command line arguments
        """
        self.logger.info("Getting account information")
        
        try:
            account_info = self.client.get_account_info()
            self.print_account_info(account_info)
        except Exception as e:
            self.logger.error(f"Failed to get account info: {str(e)}")
            print(f"Error: Failed to get account information - {str(e)}")
    
    def run(self):
        """Run the CLI application."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        # Setup environment
        self.setup_environment(args.log_level)
        
        # Handle commands
        if args.command == 'order':
            self.handle_order_command(args)
        elif args.command == 'status':
            self.handle_status_command(args)
        elif args.command == 'cancel':
            self.handle_cancel_command(args)
        elif args.command == 'account':
            self.handle_account_command(args)
        else:
            parser.print_help()
        
        # Cleanup
        if self.client:
            self.client.close()


def main():
    """Main entry point for the CLI."""
    try:
        cli = TradingBotCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
