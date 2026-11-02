"""Command-Line Interface (CLI) for Novus Quantitative Trading Bot."""

from __future__ import annotations

import argparse
import json
import sys

from .bot_core import GLOBAL_QUANT_BOT


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NovusMundus Quantitative Trading Bot CLI v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # 1. Status
    subparsers.add_parser("status", help="Muestra el estado en vivo del bot, balance y posiciones")

    # 2. Backtest
    bt_parser = subparsers.add_parser("backtest", help="Ejecuta backtesting cuantitativo con métricas")
    bt_parser.add_argument("--symbol", default="BTCUSDT", help="Símbolo a testear (BTCUSDT, ETHUSDT, NVDA, AAPL, IBE.MC, EURUSD)")
    bt_parser.add_argument(
        "--strategy",
        default="VWAP_MEAN_REVERSION",
        choices=["VWAP_MEAN_REVERSION", "MOMENTUM_EMA_RSI", "DYNAMIC_GRID"],
        help="Estrategia a evaluar",
    )
    bt_parser.add_argument("--count", type=int, default=120, help="Número de velas históricas")

    # 3. Trade
    tr_parser = subparsers.add_parser("trade", help="Ejecuta una orden de trading manual/algorítmica")
    tr_parser.add_argument("--symbol", required=True, help="Símbolo del activo")
    tr_parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Lado de la orden")
    tr_parser.add_argument("--qty", type=float, required=True, help="Cantidad a operar")
    tr_parser.add_argument("--price", type=float, default=None, help="Precio límite opcional")

    # 4. Autopilot
    ap_parser = subparsers.add_parser("autopilot", help="Activa o desactiva el piloto automático autónomo")
    ap_parser.add_argument("--toggle", action="store_true", help="Alternar estado de autopilot")

    # 5. Audit
    subparsers.add_parser("audit", help="Audita criptográficamente la cadena de bloques del ledger")

    args = parser.parse_args()

    if not args.command or args.command == "status":
        rep = GLOBAL_QUANT_BOT.get_status_report()
        print("\n=======================================================")
        print("🤖  NOVUS QUANTITATIVE TRADING BOT · STATUS REPORT")
        print("=======================================================")
        print(f"Estado Autopilot:    {'🟢 ACTIVO (Autónomo)' if rep['autopilot'] else '🟡 EN PAUSA'}")
        print(f"Estrategia Activa:   {rep['active_strategy']}")
        print(f"Balance Disponible:  {rep['cash_eur']:,.2f} €")
        print(f"Valor en Activos:    {rep['holdings_eur']:,.2f} €")
        print(f"Patrimonio Total:    {rep['total_equity_eur']:,.2f} €")
        print(f"PnL Acumulado:       {rep['total_pnl_eur']:+,.2f} €")
        print(f"Tasa de Acierto:     {rep['win_rate_pct']:.1f}% ({rep['total_trades']} operaciones)")
        print(f"Auditoría Ledger:    {rep['ledger_audit']['status']} ({rep['ledger_audit']['blocks_verified']} bloques)")
        print("\n--- POSICIONES ABIERTAS ---")
        if rep["open_positions"]:
            for s, pos in rep["open_positions"].items():
                print(f"  • {s}: {pos['qty']} @ {pos['entry_price']} € (Actual: {pos['current_price']} €)")
        else:
            print("  (Ninguna posición abierta)")

        print("\n--- PRECIOS Y SEÑALES EN TIEMPO REAL ---")
        for sym, tick in list(rep["live_ticks"].items())[:6]:
            print(f"  • {sym:8s}: {tick['price']:<10} | VWAP: {tick['vwap']:<10} | Señal: {tick['signal']:4s} ({tick['confidence_pct']}%)")
        print("=======================================================\n")

    elif args.command == "backtest":
        print(f"\n📊 Ejecutando Backtest para {args.symbol} con {args.strategy} ({args.count} velas)...")
        res = GLOBAL_QUANT_BOT.run_backtest(
            symbol=args.symbol, strategy_type=args.strategy, candle_count=args.count
        )
        print("\n=======================================================")
        print(f"📈  INFORME DE RENDIMIENTO CUANTITATIVO · {res.symbol}")
        print("=======================================================")
        print(f"Estrategia:          {res.strategy}")
        print(f"Período:             {res.start_date} -> {res.end_date}")
        print(f"Capital Inicial:     {res.initial_capital_eur:,.2f} €")
        print(f"Patrimonio Final:    {res.final_equity_eur:,.2f} €")
        print(f"Retorno Total:       {res.total_return_pct:+,.2f}%")
        print(f"Ratio de Sharpe:     {res.sharpe_ratio:.2f}")
        print(f"Ratio de Sortino:    {res.sortino_ratio:.2f}")
        print(f"Max Drawdown:        {res.max_drawdown_pct:.2f}%")
        print(f"Factor de Ganancia:  {res.profit_factor:.2f}")
        print(f"Tasa de Aciertos:    {res.win_rate_pct:.1f}% ({res.winning_trades} ganadoras / {res.losing_trades} perdedoras)")
        print(f"Operaciones Totales: {res.total_trades}")
        print("=======================================================\n")

    elif args.command == "trade":
        print(f"\n⚡ Ejecutando orden {args.side.upper()} {args.qty} {args.symbol}...")
        try:
            trade = GLOBAL_QUANT_BOT.execute_trade(
                symbol=args.symbol, side=args.side, qty=args.qty, price=args.price
            )
            print("✅ Orden ejecutada y liquidada con éxito:")
            print(f"  ID de Operación:  {trade.trade_id}")
            print(f"  Precio Llenado:   {trade.price}")
            print(f"  Monto Total:      {trade.amount_cents / 100:.2f} € (Comisión: {trade.execution_fee_cents / 100:.2f} €)")
            print(f"  Hash del Bloque:  {trade.block_hash}")
        except Exception as e:
            print(f"❌ Error al ejecutar orden: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "autopilot":
        status = GLOBAL_QUANT_BOT.toggle_autopilot()
        print(f"\n🤖 Autopilot ahora está: {'🟢 ACTIVADO (Autónomo)' if status else '🟡 PAUSADO'}\n")

    elif args.command == "audit":
        audit = GLOBAL_QUANT_BOT.execution.verify_ledger_integrity()
        print("\n=======================================================")
        print("🔐  CERTIFICACIÓN CRIPTOGRÁFICA DE LIBRO CONTABLE")
        print("=======================================================")
        print(f"Estado:              {audit['status']}")
        print(f"Bloques Validados:   {audit.get('blocks_verified', 0)}")
        if 'head_hash' in audit:
            print(f"Hash Cabecera (SHA): {audit['head_hash']}")
        print("=======================================================\n")


if __name__ == "__main__":
    main()
