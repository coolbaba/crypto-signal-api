from flask import Blueprint, jsonify, request
from src.services.signal_analyzer import signal_analyzer

signals_bp = Blueprint('signals', __name__)

@signals_bp.route('/api/signals/start', methods=['POST'])
def start_analysis():
    """Sinyal analizini başlatır"""
    try:
        result = signal_analyzer.start_analysis()
        if result:
            return jsonify({
                'success': True,
                'message': 'Sinyal analizi başlatıldı'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Sinyal analizi zaten çalışıyor'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/stop', methods=['POST'])
def stop_analysis():
    """Sinyal analizini durdurur"""
    try:
        result = signal_analyzer.stop_analysis()
        if result:
            return jsonify({
                'success': True,
                'message': 'Sinyal analizi durduruldu'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Sinyal analizi zaten durmuş'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/run-once', methods=['POST'])
def run_analysis_once():
    """Tek seferlik analiz çalıştırır"""
    try:
        signal_analyzer.run_analysis_once()
        return jsonify({
            'success': True,
            'message': 'Tek seferlik analiz tamamlandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/status', methods=['GET'])
def get_analysis_status():
    """Analiz durumunu döndürür"""
    try:
        status = signal_analyzer.get_analysis_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/active', methods=['GET'])
def get_active_signals():
    """Aktif sinyalleri döndürür"""
    try:
        signals = signal_analyzer.get_active_signals()
        return jsonify({
            'success': True,
            'data': signals
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/history', methods=['GET'])
def get_signal_history():
    """Sinyal geçmişini döndürür"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = signal_analyzer.get_signal_history(limit)
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/portfolio', methods=['GET'])
def get_portfolio_status():
    """Portföy durumunu döndürür"""
    try:
        portfolio = signal_analyzer.get_portfolio_status()
        return jsonify({
            'success': True,
            'data': portfolio
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@signals_bp.route('/api/signals/notifications', methods=['GET'])
def get_notifications():
    """Son bildirimleri döndürür"""
    try:
        limit = request.args.get('limit', 20, type=int)
        notifications = signal_analyzer.get_notifications(limit)
        return jsonify({
            'success': True,
            'data': notifications
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

