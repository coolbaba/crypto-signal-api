import os
import time
import requests
from datetime import datetime
import pytz
import logging
import threading
import json
from typing import Dict, List, Optional

# Türkiye saat dilimi
tz = pytz.timezone("Europe/Istanbul")

class SignalAnalyzer:
    def __init__(self):
        # WaveTrend parametreleri
        self.n1 = 10
        self.n2 = 21
        self.osLevel1 = -70
        self.sellLevel = 65
        
        # Sinyal verilerini saklamak için
        self.signal_prices = {}
        self.entry_times = {}
        self.entry_dates = {}
        self.profit_triggered = {}
        self.profit_times = {}
        self.profit_dates = {}
        self.trend_end_times = {}
        self.trend_end_dates = {}
        self.total_profit_percent = {}
        
        # Dashboard için veri listeleri
        self.active_signals = []
        self.signal_history = []
        self.notifications = []
        
        # Analiz durumu
        self.analysis_running = False
        self.analysis_thread = None
        
        # Kripto sembolleri listesi
        self.crypto_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'DOTUSDT', 'MATICUSDT', 'AVAXUSDT', 'DOGEUSDT', 'LUNAUSDT',
            'LINKUSDT', 'LTCUSDT', 'XRPUSDT', 'ATOMUSDT', 'ALGOUSDT'
        ]
        
        # Logging ayarları
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_turkish_time(self):
        """Türkiye saatini döndürür"""
        return datetime.now(tz).strftime("%H:%M")
    
    def get_turkish_date(self):
        """Türkiye tarihini döndürür"""
        return datetime.now(tz).strftime("%d-%m-%Y")
    
    def get_binance_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> Optional[List[Dict]]:
        """Binance API'sinden gerçek veri çeker"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Veriyi pandas benzeri formata dönüştür
            formatted_data = []
            for kline in data:
                formatted_data.append({
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'timestamp': int(kline[0])
                })
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Binance veri çekme hatası {symbol}: {e}")
            return None
    
    def calculate_wavetrend(self, data: List[Dict]) -> List[Dict]:
        """WaveTrend indikatörünü hesaplar (orijinal koddan uyarlandı)"""
        if not data or len(data) < max(self.n1, self.n2):
            return data

        # AP (Average Price) hesaplama
        for i, row in enumerate(data):
            data[i]['ap'] = (row['high'] + row['low'] + row['close']) / 3

        # ESA (Exponential Smoothed Average) hesaplama
        alpha1 = 2 / (self.n1 + 1)
        esa = data[0]['ap']
        data[0]['esa'] = esa
        
        for i in range(1, len(data)):
            esa = alpha1 * data[i]['ap'] + (1 - alpha1) * esa
            data[i]['esa'] = esa

        # D hesaplama
        d = abs(data[0]['ap'] - data[0]['esa'])
        data[0]['d'] = d
        
        for i in range(1, len(data)):
            d = alpha1 * abs(data[i]['ap'] - data[i]['esa']) + (1 - alpha1) * d
            data[i]['d'] = d

        # CI (Commodity Index) hesaplama
        for i, row in enumerate(data):
            if row['d'] != 0:
                data[i]['ci'] = (row['ap'] - row['esa']) / (0.015 * row['d'])
            else:
                data[i]['ci'] = 0

        # WT1 (WaveTrend) hesaplama
        alpha2 = 2 / (self.n2 + 1)
        wt1 = data[0]['ci']
        data[0]['wt1'] = wt1
        
        for i in range(1, len(data)):
            wt1 = alpha2 * data[i]['ci'] + (1 - alpha2) * wt1
            data[i]['wt1'] = wt1

        return data
    
    def add_notification(self, notification_type: str, symbol: str, message: str, data: Dict = None):
        """Dashboard'a bildirim ekler"""
        notification = {
            'id': f"{symbol}_{notification_type}_{int(time.time())}",
            'type': notification_type,
            'symbol': symbol,
            'message': message,
            'time': self.get_turkish_time(),
            'date': self.get_turkish_date(),
            'timestamp': time.time(),
            'data': data or {}
        }
        
        self.notifications.append(notification)
        self.signal_history.append(notification)
        
        # Son 100 bildirimi tut
        if len(self.notifications) > 100:
            self.notifications = self.notifications[-100:]
        
        self.logger.info(f"Dashboard bildirimi: {message}")
    
    def check_signals(self, symbol: str):
        """Belirli bir sembol için sinyal kontrolü yapar (orijinal koddan uyarlandı)"""
        try:
            self.logger.info(f"Veri alınıyor: {symbol}")
            
            # Gerçek veri çek
            data = self.get_binance_data(symbol)
            if not data:
                return
            
            # WaveTrend hesapla
            data = self.calculate_wavetrend(data)
            
            latest_row = data[-1]
            close_price = latest_row['close']
            wt1_value = latest_row['wt1']
            
            current_time = self.get_turkish_time()
            current_date = self.get_turkish_date()
            
            # WT alt bandına dokunma kontrolü (ALIM SİNYALİ)
            if wt1_value <= self.osLevel1 and symbol not in self.signal_prices:
                self.signal_prices[symbol] = close_price
                self.entry_times[symbol] = current_time
                self.entry_dates[symbol] = current_date
                
                message = f"🚀 ALIM SİNYALİ: {symbol} - Fiyat: {close_price:.6f}"
                
                signal_data = {
                    'type': 'BUY',
                    'symbol': symbol,
                    'price': close_price,
                    'wt1': wt1_value,
                    'time': current_time,
                    'date': current_date,
                    'message': message,
                    'strength': abs(wt1_value),
                    'id': f"{symbol}_buy_{int(time.time())}"
                }
                
                self.active_signals.append(signal_data)
                self.add_notification('BUY', symbol, message, signal_data)
            
            # %10 kâr kontrolü
            if symbol in self.signal_prices:
                entry_price = self.signal_prices[symbol]
                profit_percent = ((close_price - entry_price) / entry_price) * 100
                
                if profit_percent >= 10 and symbol not in self.profit_triggered:
                    self.profit_triggered[symbol] = True
                    self.profit_times[symbol] = current_time
                    self.profit_dates[symbol] = current_date
                    
                    message = f"🎉 %10 KÂR EDİLDİ: {symbol} - Kâr: %{profit_percent:.2f}"
                    
                    profit_data = {
                        'type': 'PROFIT',
                        'symbol': symbol,
                        'price': close_price,
                        'entry_price': entry_price,
                        'profit_percent': profit_percent,
                        'time': current_time,
                        'date': current_date,
                        'entry_time': self.entry_times[symbol],
                        'entry_date': self.entry_dates[symbol],
                        'message': message,
                        'id': f"{symbol}_profit_{int(time.time())}"
                    }
                    
                    self.add_notification('PROFIT', symbol, message, profit_data)
                
                # WaveTrend satış seviyesine geldiğinde (TREND SONU)
                if symbol in self.profit_triggered and wt1_value >= self.sellLevel:
                    self.trend_end_times[symbol] = current_time
                    self.trend_end_dates[symbol] = current_date
                    total_profit = ((close_price - entry_price) / entry_price) * 100
                    self.total_profit_percent[symbol] = total_profit
                    
                    message = f"⚠️ TREND SONUNA GELİNDİ: {symbol} - Toplam Kâr: %{total_profit:.2f}"
                    
                    sell_data = {
                        'type': 'SELL',
                        'symbol': symbol,
                        'price': close_price,
                        'entry_price': entry_price,
                        'total_profit': total_profit,
                        'time': current_time,
                        'date': current_date,
                        'entry_time': self.entry_times[symbol],
                        'entry_date': self.entry_dates[symbol],
                        'wt1': wt1_value,
                        'message': message,
                        'id': f"{symbol}_sell_{int(time.time())}"
                    }
                    
                    # Aktif sinyallerden kaldır
                    self.active_signals = [s for s in self.active_signals if s['symbol'] != symbol]
                    self.add_notification('SELL', symbol, message, sell_data)
                    
                    # Verileri temizle
                    self._cleanup_symbol_data(symbol)
                    
        except Exception as e:
            self.logger.error(f"Sinyal kontrolü hatası {symbol}: {e}")
            time.sleep(5)
    
    def _cleanup_symbol_data(self, symbol: str):
        """Sembol verilerini temizler"""
        data_dicts = [
            self.signal_prices, self.entry_times, self.entry_dates,
            self.profit_triggered, self.profit_times, self.profit_dates,
            self.trend_end_times, self.trend_end_dates, self.total_profit_percent
        ]
        
        for data_dict in data_dicts:
            data_dict.pop(symbol, None)
    
    def run_analysis_loop(self):
        """Ana analiz döngüsü (orijinal koddan uyarlandı)"""
        self.logger.info("Sinyal analizi başlatıldı")
        
        while self.analysis_running:
            try:
                for symbol in self.crypto_symbols:
                    if not self.analysis_running:
                        break
                    
                    self.check_signals(symbol)
                    time.sleep(1)  # Semboller arası bekleme
                
                if self.analysis_running:
                    time.sleep(600)  # 10 dakika bekleme (orijinal kodda 600 saniye)
                    
            except Exception as e:
                self.logger.error(f"Analiz döngüsü hatası: {e}")
                time.sleep(60)
        
        self.logger.info("Sinyal analizi durduruldu")
    
    def start_analysis(self):
        """Analizi başlatır"""
        if not self.analysis_running:
            self.analysis_running = True
            self.analysis_thread = threading.Thread(target=self.run_analysis_loop, daemon=True)
            self.analysis_thread.start()
            self.logger.info("Sinyal analizi başlatıldı")
            return True
        return False
    
    def stop_analysis(self):
        """Analizi durdurur"""
        if self.analysis_running:
            self.analysis_running = False
            if self.analysis_thread:
                self.analysis_thread.join(timeout=5)
            self.logger.info("Sinyal analizi durduruldu")
            return True
        return False
    
    def run_analysis_once(self):
        """Tek seferlik analiz çalıştırır"""
        self.logger.info("Tek seferlik analiz başlatıldı")
        
        for symbol in self.crypto_symbols:
            self.check_signals(symbol)
            time.sleep(0.5)
        
        self.logger.info("Tek seferlik analiz tamamlandı")
    
    def get_analysis_status(self) -> Dict:
        """Analiz durumunu döndürür"""
        return {
            'analysis_running': self.analysis_running,
            'active_signals_count': len(self.active_signals),
            'total_signals_count': len(self.signal_history),
            'portfolio_count': len(self.signal_prices)
        }
    
    def get_active_signals(self) -> List[Dict]:
        """Aktif sinyalleri döndürür"""
        return self.active_signals
    
    def get_signal_history(self, limit: int = 50) -> List[Dict]:
        """Sinyal geçmişini döndürür"""
        return self.signal_history[-limit:]
    
    def get_portfolio_status(self) -> List[Dict]:
        """Portföy durumunu döndürür"""
        portfolio = []
        
        for symbol, entry_price in self.signal_prices.items():
            try:
                data = self.get_binance_data(symbol, limit=1)
                if data:
                    current_price = data[-1]['close']
                    profit_percent = ((current_price - entry_price) / entry_price) * 100
                    
                    portfolio.append({
                        'symbol': symbol,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'profit_percent': profit_percent,
                        'entry_time': self.entry_times.get(symbol, ''),
                        'entry_date': self.entry_dates.get(symbol, ''),
                        'status': 'profit' if symbol in self.profit_triggered else 'active'
                    })
            except Exception as e:
                self.logger.error(f"Portföy durumu hatası {symbol}: {e}")
        
        return portfolio
    
    def get_notifications(self, limit: int = 20) -> List[Dict]:
        """Son bildirimleri döndürür"""
        return self.notifications[-limit:]

# Global sinyal analizörü instance
signal_analyzer = SignalAnalyzer()

