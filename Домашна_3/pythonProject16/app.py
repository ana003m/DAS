from flask import Flask, jsonify, request
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/api/calculate', methods=['POST'])
def calculate_indicators():
    data = request.json
    prices = data.get("prices", [])
    period = data.get("period", len(prices))

    if len(prices) < 2:
        return jsonify({"error": "Not enough data to calculate indicators"}), 400


    def calculate_rsi(prices):
        gains, losses = 0, 0
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains += change
            else:
                losses -= change
        avg_gain = gains / len(prices)
        avg_loss = losses / len(prices)
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_momentum(prices):
        return prices[-1] - prices[0]

    def calculate_williams(prices):
        high, low, close = max(prices), min(prices), prices[-1]
        return ((high - close) / (high - low)) * -100 if high != low else "N/A"

    def calculate_stochastic(prices):
        high, low, close = max(prices), min(prices), prices[-1]
        return ((close - low) / (high - low)) * 100 if high != low else "N/A"

    def calculate_ultimate(prices):
        high, low, close = max(prices), min(prices), prices[-1]
        return ((close - low) / (high - low)) * 100 if high != low else "N/A"

    def calculate_sma(prices, period):
        return sum(prices[-period:]) / period if len(prices) >= period else "N/A"

    def calculate_ema(prices, period):
        if len(prices) < period:
            return "N/A"
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def calculate_wma(prices, period):
        if len(prices) < period:
            return "N/A"
        weights = list(range(1, period + 1))
        weighted_sum = sum(p * w for p, w in zip(prices[-period:], weights))
        return weighted_sum / sum(weights)

    def calculate_hma(prices, period):
        if len(prices) < period:
            return "N/A"
        half_period = math.floor(period / 2)
        sqrt_period = math.floor(math.sqrt(period))
        wma_half = calculate_wma(prices, half_period)
        wma_full = calculate_wma(prices, period)
        if isinstance(wma_half, str) or isinstance(wma_full, str):
            return "N/A"
        diff = 2 * wma_half - wma_full
        return diff

    def calculate_tma(prices, period):
        if len(prices) < period:
            return "N/A"
        first_sma = [sum(prices[i:i + period]) / period for i in range(len(prices) - period + 1)]
        second_sma = [sum(first_sma[i:i + period]) / period for i in range(len(first_sma) - period + 1)]
        return sum(second_sma[-period:]) / period if len(second_sma) >= period else "N/A"

    def make_recommendation(indicators):
        buy_signals, sell_signals = 0, 0
        rsi, momentum, williams, stochastic, ultimate = indicators["RSI"], indicators["Momentum"], indicators[
            "Williams"], indicators["Stochastic"], indicators["Ultimate"]

        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1

        if momentum > 0:
            buy_signals += 1
        elif momentum < 0:
            sell_signals += 1

        if williams < -80:
            buy_signals += 1
        elif williams > -20:
            sell_signals += 1

        if stochastic < 20:
            buy_signals += 1
        elif stochastic > 80:
            sell_signals += 1

        if ultimate < 30:
            buy_signals += 1
        elif ultimate > 70:
            sell_signals += 1

        if buy_signals > sell_signals:
            return "Buy"
        elif sell_signals > buy_signals:
            return "Sell"
        return "Hold"

    # Calculate indicators
    indicators = {
        "RSI": calculate_rsi(prices),
        "Momentum": calculate_momentum(prices),
        "Williams": calculate_williams(prices),
        "Stochastic": calculate_stochastic(prices),
        "Ultimate": calculate_ultimate(prices),
        "SMA": calculate_sma(prices, period),
        "EMA": calculate_ema(prices, period),
        "WMA": calculate_wma(prices, period),
        "HMA": calculate_hma(prices, period),
        "TMA": calculate_tma(prices, period)
    }

    indicators["Recommendation"] = make_recommendation(indicators)

    return jsonify(indicators)

if __name__ == '__main__':
    app.run(debug=True)
