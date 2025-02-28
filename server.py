from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import json
import os
import ollama
from config import COINMARKETCAP_API_KEY, OLLAMA_HOST  # Import OLLAMA_HOST as well

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Fetch crypto data from Binance
def fetch_binance_data(crypto_symbol):
    symbol = f"{crypto_symbol.upper()}USDT"  
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            'price': float(data['lastPrice']),
            'percent_change_24h': float(data['priceChangePercent']),
            'volume': float(data['volume']),
            'quote_volume': float(data['quoteVolume'])
        }
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching Binance data for {symbol}: {e}")
        return None

# Fetch crypto data from Bybit
def fetch_bybit_data(crypto_symbol):
    symbol = f"{crypto_symbol.upper()}USDT"
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        ticker = data['result']['list'][0]  # Bybit returns a list of tickers
        return {
            'price': float(ticker['lastPrice']),
            'percent_change_24h': float(ticker['price24hPcnt']) * 100,  # Convert to percentage
            'volume': float(ticker['volume24h'])
        }
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching Bybit data for {symbol}: {e}")
        return None

# Fetch crypto data from CoinMarketCap
def fetch_coinmarketcap_data(crypto_symbol):
    symbol = crypto_symbol.upper()
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
        params = {"symbol": symbol, "convert": "USD"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        crypto_data = data["data"][symbol]["quote"]["USD"]
        return {
            'price': float(crypto_data['price']),
            'market_cap': float(crypto_data['market_cap']),
            'volume': float(crypto_data['volume_24h']),
            'percent_change_24h': float(crypto_data['percent_change_24h'])
        }
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching CoinMarketCap data for {symbol}: {e}")
        return None

# Add a fallback prediction method for when Ollama is unavailable
def get_fallback_prediction(crypto_symbol, model_data):
    binance_data = model_data.get("binance", {})
    current_price = binance_data.get('price', 0)
    change_24h = binance_data.get('percent_change_24h', 0)
    
    prediction_text = (
        f"Based on the current data for {crypto_symbol}, the price is ${current_price:.4f}. "
        f"In the last 24 hours, there has been a {change_24h:.2f}% change. "
        f"Due to temporary issues with our prediction service, detailed analysis is unavailable. "
        f"Please try again later for AI-powered predictions."
    )
    
    return {"prediction_text": prediction_text}

# Get prediction from Ollama AI
def get_crypto_prediction(crypto_symbol, model_data):
    model_name = "deepseek-r1:1.5b"
    
    binance_data = model_data.get("binance", {})
    bybit_data = model_data.get("bybit", {})
    coinmarketcap_data = model_data.get("coinmarketcap", {})
    
    instruction = (
        f"You are an AI predicting {crypto_symbol.upper()}/USDT prices based on real-time data. "
        "Here is the latest market data. Analyze and predict the future price:\n\n"
        f"1. Binance: Price: {binance_data.get('price', 'N/A')}, 24h Change: {binance_data.get('percent_change_24h', 'N/A')}%, "
        f"Volume: {binance_data.get('volume', 'N/A')}, Quote Volume: {binance_data.get('quote_volume', 'N/A')}\n"
        f"2. Bybit: Price: {bybit_data.get('price', 'N/A')}, 24h Change: {bybit_data.get('percent_change_24h', 'N/A')}%, "
        f"Volume: {bybit_data.get('volume', 'N/A')}\n"
        f"3. CoinMarketCap: Price: {coinmarketcap_data.get('price', 'N/A')}, Market Cap: {coinmarketcap_data.get('market_cap', 'N/A')}, "
        f"Volume: {coinmarketcap_data.get('volume', 'N/A')}, 24h Change: {coinmarketcap_data.get('percent_change_24h', 'N/A')}\n\n"
        f"Predict {crypto_symbol.upper()}'s price based on the above data.\n"
        "Try to predict at which price the next major resistance will be and the price will reverse.\n"
        f"Predict a 99% confidence interval for {crypto_symbol.upper()}'s price in the next 4 hours."
    )

    try:
        # Use direct HTTP request to Ollama API with streaming set to FALSE
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model_name,
                "prompt": instruction,
                "stream": False  # Set to False to get a single complete response
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Check if response content exists before trying to decode
        if not response.text:
            print("Empty response received from Ollama API")
            return {"error": "Empty response from AI service. Please try again."}
            
        try:
            result = response.json()
            return {"prediction_text": result.get('response', 'No prediction available')}
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error with Ollama API: {e}")
            print(f"Response text: {response.text[:200]}...")  # Print first 200 chars of response for debugging
            return {"error": "Failed to decode AI response. Please try again later."}
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error with Ollama API: {e}")
        return {"error": "Connection to AI service failed. Please try again later."}
    except requests.exceptions.Timeout as e:
        print(f"Timeout error with Ollama API: {e}")
        return {"error": "AI service request timed out. Please try again later."}
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error with Ollama API: {e}")
        status_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else 'unknown'
        return {"error": f"AI service returned an error (status {status_code}). Please try again later."}
    except Exception as e:
        print(f"Unexpected error with Ollama API: {e}")
        print(f"Falling back to basic prediction due to error: {e}")
        return get_fallback_prediction(crypto_symbol, model_data)

# Serve the HTML frontend
@app.route('/')
def index():
    try:
        return render_template('index.html')  # You'll need to create this file
    except Exception as e:
        return jsonify({"error": f"Failed to load index.html: {e}"}), 500

# Endpoint to fetch market data based on user input
@app.route('/api/crypto-data', methods=['POST'])
def get_crypto_data():
    try:
        data = request.json
        crypto_symbol = data.get('crypto_symbol')
        if not crypto_symbol:
            return jsonify({"error": "No cryptocurrency symbol provided"}), 400

        binance_data = fetch_binance_data(crypto_symbol)
        bybit_data = fetch_bybit_data(crypto_symbol)
        coinmarketcap_data = fetch_coinmarketcap_data(crypto_symbol)

        # Check if any data fetch failed
        if not any([binance_data, bybit_data, coinmarketcap_data]):
            return jsonify({
                "error": "Failed to fetch data from all sources",
                "binance": binance_data is not None,
                "bybit": bybit_data is not None,
                "coinmarketcap": coinmarketcap_data is not None
            }), 500

        combined_data = {
            "binance": binance_data or {},
            "bybit": bybit_data or {},
            "coinmarketcap": coinmarketcap_data or {}
        }

        return jsonify({"live_data": combined_data, "crypto_symbol": crypto_symbol})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for predictions with improved error handling
@app.route('/api/crypto-prediction', methods=['POST'])
def get_prediction():
    try:
        data = request.json
        if not data or 'live_data' not in data or 'crypto_symbol' not in data:
            return jsonify({"error": "No market data or crypto symbol provided"}), 400
        
        crypto_symbol = data['crypto_symbol']
        combined_data = data['live_data']
        
        # Set a longer timeout for the entire request handling
        prediction = get_crypto_prediction(crypto_symbol, combined_data)
        
        # Check if prediction contains an error
        if "error" in prediction:
            return jsonify({
                "prediction": prediction, 
                "crypto_symbol": crypto_symbol,
                "status": "error"
            }), 200  # Return 200 but with error status in the response
        
        return jsonify({
            "prediction": prediction, 
            "crypto_symbol": crypto_symbol,
            "status": "success"
        })
    except Exception as e:
        print(f"Prediction failed: {str(e)}")
        return jsonify({
            "error": f"Prediction failed: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=5000)