# Binance Futures Testnet Trading Bot

A simplified Python trading bot that can place orders on Binance Futures Testnet (USDT-M) with proper logging, error handling, and a clean CLI interface.

## Features

- **Order Placement**: Place Market and Limit orders on Binance Futures Testnet
- **Order Management**: Check order status and cancel existing orders
- **Input Validation**: Comprehensive validation of user input and order parameters
- **Structured Logging**: Detailed logging of API requests, responses, and errors
- **CLI Interface**: Clean command-line interface with argparse
- **Error Handling**: Robust exception handling for network and API errors
- **Account Information**: View account balances and positions

## Requirements

- Python 3.7+
- Binance Futures Testnet account
- API credentials (API Key & Secret)

## Setup

### 1. Binance Futures Testnet Account

1. Register and activate a Binance Futures Testnet account
2. Generate API credentials from the Binance Testnet dashboard
3. Ensure your testnet account has sufficient USDT balance for trading

### 2. Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

Set your API credentials as environment variables:

**Windows:**
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

**Linux/Mac:**
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

**Or create a `.env` file:**
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

## Usage

### Basic Commands

#### Place a Market Order
```bash
python main.py order BTCUSDT BUY MARKET 0.001
```

#### Place a Limit Order
```bash
python main.py order BTCUSDT SELL LIMIT 0.001 65000.00
```

#### Get Order Status
```bash
python main.py status BTCUSDT 123456789
```

#### Cancel an Order
```bash
python main.py cancel BTCUSDT 123456789
```

#### Get Account Information
```bash
python main.py account
```

### Advanced Options

#### Set Logging Level
```bash
python main.py --log-level DEBUG order BTCUSDT BUY MARKET 0.001
```

#### Get Help
```bash
python main.py --help
python main.py order --help
```

## Command Examples

### Market Buy Order
```bash
python main.py order BTCUSDT BUY MARKET 0.001
```
Output:
```
==================================================
ORDER REQUEST SUMMARY
==================================================
Symbol:     BTCUSDT
Side:       BUY
Type:       MARKET
Quantity:   0.001
==================================================

==================================================
ORDER RESPONSE
==================================================
Status:     SUCCESS
Order ID:   123456789
Symbol:     BTCUSDT
Side:       BUY
Type:       MARKET
Quantity:   0.001
Status:     FILLED
Executed:   0.001
Avg Price:  64500.50
Message:    Order placed successfully
==================================================
```

### Limit Sell Order
```bash
python main.py order BTCUSDT SELL LIMIT 0.001 65000.00
```
Output:
```
==================================================
ORDER REQUEST SUMMARY
==================================================
Symbol:     BTCUSDT
Side:       SELL
Type:       LIMIT
Quantity:   0.001
Price:      65000.0
==================================================

==================================================
ORDER RESPONSE
==================================================
Status:     SUCCESS
Order ID:   123456790
Symbol:     BTCUSDT
Side:       SELL
Type:       LIMIT
Quantity:   0.001
Price:      65000.0
Status:     NEW
Message:    Order placed successfully
==================================================
```

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package initialization
│   ├── client.py            # Binance API client wrapper
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # Input validation
│   ├── logging_config.py    # Logging configuration
│   └── cli.py              # CLI interface
├── main.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── logs/                   # Log files directory (auto-created)
```

## API Endpoints Used

- `/fapi/v2/account` - Get account information
- `/fapi/v1/exchangeInfo` - Get symbol information
- `/fapi/v1/order` - Place new order
- `/fapi/v1/order` - Get order status
- `/fapi/v1/order` - Cancel order

## Logging

The bot creates detailed log files in the `logs/` directory:

- Log files are named with timestamp: `trading_bot_YYYYMMDD_HHMMSS.log`
- Logs include API requests, responses, validation errors, and system events
- Log rotation: 10MB max file size with 5 backup files
- Console output shows INFO level and above
- File logs include DEBUG level information

### Log Levels

- **DEBUG**: Detailed API request/response data
- **INFO**: Order requests, responses, and important events
- **WARNING**: Non-critical issues and validation warnings
- **ERROR**: API errors, validation failures, and exceptions

## Error Handling

The bot includes comprehensive error handling for:

- **Network Errors**: Connection timeouts, DNS failures
- **API Errors**: Invalid credentials, insufficient balance, invalid symbols
- **Validation Errors**: Invalid input parameters, missing required fields
- **Symbol Validation**: Quantity/price precision, minimum/maximum limits

## Validation Features

### Input Validation
- Symbol format validation (e.g., BTCUSDT)
- Order side validation (BUY/SELL)
- Order type validation (MARKET/LIMIT)
- Quantity and price validation (positive numbers)
- Required field validation

### Symbol-Specific Validation
- Minimum/maximum quantity limits
- Price precision and tick size
- Quantity step size
- Minimum notional value

## Security Considerations

- API credentials are read from environment variables only
- Sensitive data (signatures, API keys) are redacted in logs
- No hardcoded credentials in the source code
- Uses HTTPS for all API communications

## Testing

### Test with Small Quantities
Always test with small quantities first:
```bash
python main.py order BTCUSDT BUY MARKET 0.001
```

### Check Account Balance
Verify your testnet balance before placing orders:
```bash
python main.py account
```

### Test Different Order Types
Try both market and limit orders to ensure they work correctly.

## Troubleshooting

### Common Issues

#### API Credentials Not Found
```
Error: Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables
```
**Solution**: Ensure environment variables are set correctly.

#### Invalid API Credentials
```
Error: Invalid API credentials - API key appears to be invalid (too short)
```
**Solution**: Verify your API key and secret from Binance Testnet.

#### Insufficient Balance
```
Binance API Error: Account has insufficient balance for requested action
```
**Solution**: Check your account balance and ensure you have enough USDT.

#### Invalid Symbol
```
Binance API Error: Invalid symbol
```
**Solution**: Use valid futures symbols (e.g., BTCUSDT, ETHUSDT).

#### Network Errors
```
Network error: Connection timeout
```
**Solution**: Check your internet connection and try again.

### Debug Mode
Enable debug logging for detailed troubleshooting:
```bash
python main.py --log-level DEBUG order BTCUSDT BUY MARKET 0.001
```

## Assumptions

1. User has a Binance Futures Testnet account with API credentials
2. User has sufficient USDT balance in their testnet account
3. User understands basic trading concepts (market/limit orders, buy/sell)
4. User is familiar with command-line interfaces
5. Trading is done on USDT-margined futures contracts

## Limitations

1. **Testnet Only**: Works only on Binance Futures Testnet, not mainnet
2. **Basic Orders**: Supports only MARKET and LIMIT orders (no stop-loss, OCO, etc.)
3. **No Position Management**: Does not manage leverage or position sizing
4. **No Real-time Data**: Does not provide real-time price feeds
5. **Single Account**: Designed for single account usage

## Future Enhancements (Optional Bonus Features)

Potential improvements for future versions:

1. **Additional Order Types**: Stop-Limit, OCO (One-Cancels-Other), TWAP
2. **Enhanced CLI**: Interactive menus, prompts, better UX
3. **Lightweight UI**: Simple web interface for order management
4. **Position Management**: Automatic position sizing and leverage management
5. **Price Alerts**: Price monitoring and alert system
6. **Portfolio Tracking**: Profit/loss tracking and reporting
7. **Backtesting**: Historical order testing capabilities

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the log files in the `logs/` directory
3. Verify your API credentials and testnet account status
4. Ensure you have sufficient balance for the intended trades

## License

This project is provided as-is for educational and testing purposes. Use at your own risk.

---

**Disclaimer**: This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. The author is not responsible for any financial losses incurred while using this software. Always test thoroughly on testnet before considering any real trading applications.
