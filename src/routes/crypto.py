from flask import Blueprint, jsonify, request
import random
import time
from datetime import datetime, timedelta

crypto_bp = Blueprint('crypto', __name__)

# Mock data for demonstration
MOCK_COINS = [
    {'symbol': 'BTC', 'name': 'Bitcoin'},
    {'symbol': 'ETH', 'name': 'Ethereum'},
    {'symbol': 'BNB', 'name': 'Binance Coin'},
    {'symbol': 'ADA', 'name': 'Cardano'},
    {'symbol': 'SOL', 'name': 'Solana'},
    {'symbol': 'DOT', 'name': 'Polkadot'},
    {'symbol': 'MATIC', 'name': 'Polygon'},
    {'symbol': 'AVAX', 'name': 'Avalanche'},
    {'symbol': 'DOGE', 'name': 'Dogecoin'},
    {'symbol': 'LUNA', 'name': 'Terra Luna'}
]

def generate_mock_price_data(base_price, hours=24):
    """Mock fiyat verisi üretir"""
    data = []
    current_price = base_price
    
    for i in range(hours):
        # Rastgele fiyat değişimi
        change_percent = (random.random() - 0.5) * 0.1  # %5 arası değişim
        current_price *= (1 + change_percent)
        
        data.append({
            'timestamp': int(time.time()) - (hours - i) * 3600,
            'price': round(current_price, 2),
            'volume': random.randint(500000, 2000000)
        })
    
    return data

def generate_mock_signals():
    """Mock sinyal verisi üretir"""
    signals = []
    signal_types = ['BUY', 'SELL', 'HOLD']
    indicators = [
        ['RSI', 'MACD', 'Bollinger Bands'],
        ['EMA', 'Stochastic', 'Volume'],
        ['Moving Average', 'Support/Resistance', 'Fibonacci'],
        ['Trend Lines', 'Volume Profile', 'Ichimoku']
    ]
    
    for i, coin in enumerate(MOCK_COINS[:5]):
        signal_type = random.choice(signal_types)
        base_price = random.uniform(0.1, 50000)
        
        if coin['symbol'] == 'BTC':
            base_price = 43250.50
        elif coin['symbol'] == 'ETH':
            base_price = 2650.75
        elif coin['symbol'] == 'BNB':
            base_price = 315.20
        elif coin['symbol'] == 'ADA':
            base_price = 0.52
        elif coin['symbol'] == 'SOL':
            base_price = 98.45
            
        target_multiplier = 1.1 if signal_type == 'BUY' else 0.9
        stop_multiplier = 0.95 if signal_type == 'BUY' else 1.05
        
        signals.append({
            'id': i + 1,
            'symbol': f"{coin['symbol']}/USDT",
            'type': signal_type,
            'strength': random.randint(60, 95),
            'price': base_price,
            'target': round(base_price * target_multiplier, 2),
            'stopLoss': round(base_price * stop_multiplier, 2),
            'timeframe': random.choice(['1h', '4h', '1d', '1w']),
            'accuracy': random.randint(80, 98),
            'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 60)),
            'indicators': random.choice(indicators)
        })
    
    return signals

@crypto_bp.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """Piyasa genel bakış verilerini döndürür"""
    try:
        # Mock market data
        overview = {
            'totalMarketCap': 1650000000000,  # $1.65T
            'totalVolume': 89200000000,       # $89.2B
            'marketCapChange': 2.34,
            'volumeChange': -1.45,
            'dominance': {
                'btc': 42.5,
                'eth': 18.2
            }
        }
        
        return jsonify({
            'success': True,
            'data': overview
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/top-movers', methods=['GET'])
def get_top_movers():
    """En çok kazanan ve kaybeden coin'leri döndürür"""
    try:
        gainers = [
            {'symbol': 'DOGE', 'change': 15.67, 'price': 0.085},
            {'symbol': 'ADA', 'change': 12.34, 'price': 0.52},
            {'symbol': 'DOT', 'change': 8.91, 'price': 7.23}
        ]
        
        losers = [
            {'symbol': 'LUNA', 'change': -8.45, 'price': 0.95},
            {'symbol': 'AVAX', 'change': -6.78, 'price': 38.20},
            {'symbol': 'MATIC', 'change': -5.23, 'price': 0.89}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'gainers': gainers,
                'losers': losers
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/market-data', methods=['GET'])
def get_market_data():
    """Ana piyasa verilerini döndürür"""
    try:
        market_data = [
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'price': 43250.50,
                'change': 2.45,
                'volume': '28.5B',
                'signal': 'BUY'
            },
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'price': 2650.75,
                'change': -1.23,
                'volume': '15.2B',
                'signal': 'HOLD'
            },
            {
                'symbol': 'BNB',
                'name': 'Binance Coin',
                'price': 315.20,
                'change': 4.67,
                'volume': '2.1B',
                'signal': 'BUY'
            },
            {
                'symbol': 'SOL',
                'name': 'Solana',
                'price': 98.45,
                'change': -3.21,
                'volume': '1.8B',
                'signal': 'SELL'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': market_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/signals', methods=['GET'])
def get_signals():
    """Kripto sinyallerini döndürür"""
    try:
        filter_type = request.args.get('filter', 'all')
        timeframe = request.args.get('timeframe', '1h')
        
        signals = generate_mock_signals()
        
        # Filtreleme
        if filter_type != 'all':
            signals = [s for s in signals if s['type'].lower() == filter_type.lower()]
        
        # Timestamp'i string'e çevir
        for signal in signals:
            signal['timestamp'] = signal['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'data': signals
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Portföy verilerini döndürür"""
    try:
        portfolio = [
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'amount': 0.5,
                'avgPrice': 40000,
                'currentPrice': 43250.50,
                'value': 21625.25,
                'change': 1625.25,
                'changePercent': 8.125,
                'color': '#f7931a'
            },
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'amount': 5.2,
                'avgPrice': 2500,
                'currentPrice': 2650.75,
                'value': 13783.90,
                'change': 783.90,
                'changePercent': 6.03,
                'color': '#627eea'
            },
            {
                'symbol': 'BNB',
                'name': 'Binance Coin',
                'amount': 15,
                'avgPrice': 300,
                'currentPrice': 315.20,
                'value': 4728,
                'change': 228,
                'changePercent': 5.07,
                'color': '#f3ba2f'
            },
            {
                'symbol': 'ADA',
                'name': 'Cardano',
                'amount': 1000,
                'avgPrice': 0.45,
                'currentPrice': 0.52,
                'value': 520,
                'change': 70,
                'changePercent': 15.56,
                'color': '#0033ad'
            },
            {
                'symbol': 'SOL',
                'name': 'Solana',
                'amount': 8,
                'avgPrice': 105,
                'currentPrice': 98.45,
                'value': 787.60,
                'change': -52.40,
                'changePercent': -6.24,
                'color': '#9945ff'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': portfolio
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Belirli bir coin için grafik verilerini döndürür"""
    try:
        timeframe = request.args.get('timeframe', '1d')
        
        # Base price belirleme
        base_prices = {
            'BTC': 43000,
            'ETH': 2650,
            'BNB': 315,
            'ADA': 0.52,
            'SOL': 98
        }
        
        base_price = base_prices.get(symbol.upper(), 100)
        
        # Zaman aralığına göre veri sayısı
        hours = 24 if timeframe == '1d' else 168 if timeframe == '1w' else 24
        
        chart_data = generate_mock_price_data(base_price, hours)
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/technical-indicators/<symbol>', methods=['GET'])
def get_technical_indicators(symbol):
    """Teknik indikatörleri döndürür"""
    try:
        indicators = {
            'rsi': round(random.uniform(30, 70), 1),
            'macd': random.choice(['Bullish', 'Bearish']),
            'ema20': random.uniform(40000, 45000),
            'ema50': random.uniform(38000, 42000),
            'support': random.uniform(40000, 42000),
            'resistance': random.uniform(44000, 46000),
            'bollingerUpper': random.uniform(44000, 45000),
            'bollingerLower': random.uniform(41000, 42000)
        }
        
        return jsonify({
            'success': True,
            'data': indicators
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/api/market-sentiment', methods=['GET'])
def get_market_sentiment():
    """Piyasa duyarlılığını döndürür"""
    try:
        sentiment_data = {
            'fearGreedIndex': random.randint(20, 80),
            'sentiment': random.choice(['Fear', 'Neutral', 'Greedy']),
            'socialVolume': random.randint(5000, 15000),
            'newsScore': round(random.uniform(0.3, 0.8), 2),
            'whaleActivity': random.choice(['Low', 'Medium', 'High'])
        }
        
        return jsonify({
            'success': True,
            'data': sentiment_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

