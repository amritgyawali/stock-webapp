"""
Stock Recommendation Engine
Analyzes latest NEPSE data to recommend best stocks to buy today
"""

import sys
import os
# Fix encoding on Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

from datetime import datetime, timedelta, timezone
from config import db, get_nepal_time, get_latest_trading_date, logger

def get_recommendations():
    """Get top stock recommendations for today"""
    
    nepal_now = get_nepal_time()
    
    # Get latest available dates from database
    print("[*] Analyzing available data...")
    try:
        all_prices = db.select('daily_prices', columns='*', limit=1000)
        all_predictions = db.select('predictions', columns='*', limit=1000)
        
        if not all_prices or not all_predictions:
            print("[ERROR] No data available in database")
            return None
        
        # Find unique dates
        price_dates = set(p.get('date') for p in all_prices if p.get('date'))
        pred_dates = set(p.get('prediction_date') for p in all_predictions if p.get('prediction_date'))
        
        # Find best matching date pair (most recent dates available)
        # Strategy: Use most recent prediction date with most recent price date
        trading_date = sorted(price_dates, reverse=True)[0] if price_dates else None
        prediction_date = sorted(pred_dates, reverse=True)[0] if pred_dates else None
        
        if not trading_date or not prediction_date:
            print(f"[ERROR] Incomplete data - Prices: {len(price_dates)} dates, Predictions: {len(pred_dates)} dates")
            return None
        
        prices_data = [p for p in all_prices if p.get('date') == trading_date]
        predictions_data = [p for p in all_predictions if p.get('prediction_date') == prediction_date]
        
    except Exception as e:
        logger.warning(f"Error fetching data: {e}")
        return None
    
    print(f"\n{'='*70}")
    print(f"[NEPSE STOCK RECOMMENDATION ENGINE]")
    print(f"{'='*70}")
    print(f"[Price Data Date: {trading_date}]")
    print(f"[Prediction Date: {prediction_date}]")
    print(f"[Current Nepal Time: {nepal_now.strftime('%Y-%m-%d %H:%M:%S NPT')}]")
    print(f"{'='*70}\n")
    
    if not prices_data:
        print(f"[ERROR] No price data available for {trading_date}")
        return None
    
    print(f"[+] Found {len(prices_data)} stocks with prices\n")
    
    if not predictions_data:
        print(f"[ERROR] No predictions available for {prediction_date}")
        return None
    
    # Create lookup maps
    # Note: daily_prices and predictions use stock_id (numeric), not symbol
    # Need to map through stocks table to get symbols
    price_map = {}
    for p in prices_data:
        stock_id = p.get('stock_id')
        if stock_id:
            price_map[stock_id] = p
    
    pred_map = {}
    for p in predictions_data:
        stock_id = p.get('stock_id')
        if stock_id:
            pred_map[stock_id] = p
    
    print(f"[+] Found {len(predictions_data)} predictions")
    print(f"[*] Matching IDs: {len([s for s in pred_map if s in price_map])} of {len(pred_map)} predictions have prices\n")
    
    # Get stock info
    print("[*] Fetching stock information...")
    try:
        stocks_data = db.select('stocks', columns='*', limit=1000)
    except Exception as e:
        logger.warning(f"Error fetching stocks: {e}")
        stocks_data = []
    
    stock_map = {}
    for s in stocks_data:
        stock_id = s.get('id')
        if stock_id:
            stock_map[stock_id] = s
    
    print(f"[+] Found {len(stocks_data)} companies")
    matching_all_three = len([s for s in pred_map if s in price_map and s in stock_map])
    print(f"[*] Symbols with prices + predictions + stock info: {matching_all_three}\n")
    
    # Calculate recommendations
    print(f"{'='*70}")
    print("[ANALYSIS & RECOMMENDATIONS]")
    print(f"{'='*70}\n")
    
    all_analysis = []
    
    for stock_id in pred_map:
        if stock_id not in price_map or stock_id not in stock_map:
            continue
        
        price = price_map[stock_id]
        pred = pred_map[stock_id]
        stock = stock_map[stock_id]
        
        current_close = price.get('close', 0)
        predicted_close = pred.get('predicted_close', 0)
        confidence_raw = pred.get('confidence_score', 0)
        symbol = stock.get('symbol', f'ID{stock_id}')
        
        if not current_close or not predicted_close:
            continue
        
        # Calculate metrics
        upside = ((predicted_close - current_close) / current_close) * 100
        upside_amount = predicted_close - current_close
        
        all_analysis.append({
            'symbol': symbol,
            'name': stock.get('name', ''),
            'sector': stock.get('sector', 'Others'),
            'current_price': current_close,
            'predicted_price': predicted_close,
            'upside_percent': upside,
            'upside_amount': upside_amount,
            'confidence': confidence_raw,  # Keep as 0-1 decimal for .1% formatting
            'open': price.get('open', 0),
            'high': price.get('high', 0),
            'low': price.get('low', 0),
            'volume': price.get('volume', 0),
            'qualifies': upside > 2 and confidence_raw > 0.5
        })
    
    # Sort by upside percentage
    all_analysis.sort(key=lambda x: x['upside_percent'], reverse=True)
    recommendations = [r for r in all_analysis if r['qualifies']]
    
    if not recommendations:
        print("[!] No stocks with >2% upside and >50% confidence")
        print(f"[DEBUG] Total analyzed: {len(all_analysis)}, Matched symbols: {len([r for r in all_analysis if r])}")
        print("\n[market analysis]")
        
        # Show top performers anyway
        if all_analysis:
            print(f"\nTop 5 predicted movers (regardless of confidence):\n")
            print(f"{'Symbol':<8} {'Current':<10} {'Target':<10} {'Upside %':<10} {'Confidence'}")
            print("-" * 60)
            for r in all_analysis[:5]:
                print(f"{r['symbol']:<8} Rs{r['current_price']:<9.2f} Rs{r['predicted_price']:<9.2f} {r['upside_percent']:>6.2f}% {r['confidence']:>8.2f}%")
        
        # Market statistics
        upside_pct = len([r for r in all_analysis if r['upside_percent'] > 0]) / len(all_analysis) * 100 if all_analysis else 0
        avg_upside = sum(r['upside_percent'] for r in all_analysis) / len(all_analysis) if all_analysis else 0
        print(f"\nMarket Statistics:")
        print(f"  Predicted Up: {upside_pct:.1f}% of stocks")
        print(f"  Average Upside: {avg_upside:.2f}%")
        print(f"  [INFO] Market appears bearish - investors may want to wait for better entry points")
        print()
        return
    
    # Display top 10 recommendations
    print(f"\n[TOP 10 STOCKS TO BUY TODAY]\n")
    print(f"{'Rank':<5} {'Symbol':<8} {'Company':<25} {'Price':<10} {'Target':<10} {'Upside':<10} {'Conf':<6}")
    print(f"{'-'*80}")
    
    for idx, rec in enumerate(recommendations[:10], 1):
        sym = rec['symbol']
        name = rec['name'][:23]
        curr = f"Rs {rec['current_price']:.2f}"
        target = f"Rs {rec['predicted_price']:.2f}"
        upside = f"{rec['upside_percent']:.1f}%"
        conf = f"{rec['confidence']:.0%}"
        
        print(f"{idx:<5} {sym:<8} {name:<25} {curr:<10} {target:<10} {upside:<10} {conf:<6}")
    
    # Detailed analysis for top 3
    print(f"\n{'='*70}")
    print("[DETAILED ANALYSIS - TOP 3 PICKS]")
    print(f"{'='*70}\n")
    
    for idx, rec in enumerate(recommendations[:3], 1):
        print(f"\n#{idx} {rec['symbol']} - {rec['name']}")
        print(f"   Sector: {rec['sector']}")
        print(f"   {'-' * 55}")
        print(f"   Current Price:     Rs {rec['current_price']:.2f}")
        print(f"   Predicted Target:  Rs {rec['predicted_price']:.2f}")
        print(f"   Expected Upside:   {rec['upside_percent']:.2f}% (Rs {rec['upside_amount']:.2f})")
        print(f"   Prediction Confidence: {rec['confidence']:.1%}")
        print(f"   {'-' * 55}")
        print(f"   Today's Open:      Rs {rec['open']:.2f}")
        print(f"   Today's High:      Rs {rec['high']:.2f}")
        print(f"   Today's Low:       Rs {rec['low']:.2f}")
        if rec['volume']:
            print(f"   Volume:            {rec['volume']:,.0f} shares")
        print()
    
    # Risk considerations
    print(f"{'='*70}")
    print("[IMPORTANT DISCLAIMERS]")
    print(f"{'='*70}\n")
    print("[*] This analysis is based on historical data and ML models")
    print("[*] Past performance does NOT guarantee future results")
    print("[*] Stock markets involve risk - only invest what you can afford to lose")
    print("[*] Consider your risk profile and investment horizon")
    print("[*] Do your own research before making investment decisions")
    print("[*] Consult with a financial advisor if you're new to investing")
    print()
    
    # Market summary
    print(f"{'='*70}")
    print("[MARKET SUMMARY]")
    print(f"{'='*70}\n")
    
    gainers = [r for r in recommendations if r['upside_percent'] > 10]
    moderate = [r for r in recommendations if 5 < r['upside_percent'] <= 10]
    small = [r for r in recommendations if 2 < r['upside_percent'] <= 5]
    
    print(f"Stocks with >10% upside:  {len(gainers)} stocks")
    print(f"Stocks with 5-10% upside: {len(moderate)} stocks")
    print(f"Stocks with 2-5% upside:  {len(small)} stocks")
    print(f"Total positive setups:    {len(recommendations)} stocks\n")
    
    avg_upside = sum(r['upside_percent'] for r in recommendations) / len(recommendations)
    avg_confidence = sum(r['confidence'] for r in recommendations) / len(recommendations)
    print(f"Average Expected Upside:  {avg_upside:.2f}%")
    print(f"Average Confidence:       {avg_confidence:.1%}\n")
    
    # Strategy suggestion
    print(f"{'='*70}")
    print("[SUGGESTED STRATEGY]")
    print(f"{'='*70}\n")
    
    if avg_upside > 8:
        print("[BULLISH] Market has strong positive signals")
        print("[ACTION] Consider buying top-rated stocks")
    elif avg_upside > 5:
        print("[MODERATELY BULLISH] Good opportunities with reasonable upside")
        print("[ACTION] Pick 2-3 from top picks for diversification")
    else:
        print("[NEUTRAL] Limited opportunities")
        print("[ACTION] Be selective, focus on highest confidence picks")
    
    print()
    print(f"[TIPS] Remember: Diversification reduces risk!")
    print(f"[TIPS] Don't put all money in one stock")
    print(f"[TIPS] Consider a portfolio of top-rated picks\n")
    
    return recommendations

if __name__ == '__main__':
    try:
        recommendations = get_recommendations()
        if recommendations:
            print(f"{'='*70}")
            print("[ANALYSIS COMPLETE]")
            print(f"{'='*70}\n")
    except Exception as e:
        logger.error(f"Error in recommendation engine: {e}")
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)
