# Crypto Market Sentiment Analyser

A modern web application that provides real-time cryptocurrency price data from multiple sources and AI-powered price predictions.

![Crypto Market Sentiment Analyser Screenshot]

## Features

- **Real-time Price Data**: Fetch and display crypto prices from multiple sources:
  - Binance
  - Bybit
  - CoinMarketCap
- **Market Statistics**: View 24-hour price changes, trading volumes, and market cap data
- **AI-Powered Predictions**: Generate market sentiment analysis and price predictions using Ollama AI
- **Multi-Cryptocurrency Support**: Search for any cryptocurrency by its ticker symbol (BTC, ETH, ADA, etc.)
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: Toggle between dark and light themes

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **AI Model**: Ollama with the Deepseek-r1 (1.5b) model
- **APIs**:
  - Binance API
  - Bybit API
  - CoinMarketCap API

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed locally (for AI predictions)
- CoinMarketCap API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Crypto-Price-prediction.git
   cd Crypto-Price-prediction
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `config.py` file with your CoinMarketCap API key:
   ```python
   COINMARKETCAP_API_KEY = "your_api_key_here"
   ```

4. Make sure Ollama is running locally with the Deepseek model:
   ```bash
   ollama pull deepseek-r1:1.5b
   ```

### Running the Application

Start the Flask server:
```bash
python server.py
```

The application will be available at http://localhost:5000

## Usage

1. Open the application in your web browser
2. Enter a cryptocurrency ticker symbol (e.g., BTC, ETH, ADA) in the search box
3. Click "Load" to fetch the latest market data
4. Use the "Generate Prediction" button to get an AI analysis of the price trend

## Project Structure

```
Crypto-Price-prediction/
│
├── server.py                # Flask server and API endpoints
├── config.py                # API keys and configuration
├── requirements.txt         # Python dependencies
│
├── static/
│   ├── index.css            # Stylesheet for the application
│   └── Mimesis.svg          # Logo file
│
└── templates/
    └── index.html           # Main application HTML
```

## API Endpoints

- **GET /**: Serves the main application page
- **POST /api/crypto-data**: Fetches cryptocurrency data from multiple sources
  - Request body: `{"crypto_symbol": "BTC"}`
- **POST /api/crypto-prediction**: Generates AI price predictions
  - Request body: `{"live_data": {...}, "crypto_symbol": "BTC"}`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CoinMarketCap for providing cryptocurrency market data
- Binance and Bybit for their public APIs
- Ollama team for their accessible AI models
