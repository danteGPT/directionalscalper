import threading
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table

shared_symbols_data = {}

class LiveTableManager:
    def __init__(self):
        self.table = self.generate_table()
        self.row_data = {}  # Dictionary to store row data
        self.lock = threading.Lock()

    def generate_table(self) -> Table:
        table = Table(show_header=True, header_style="bold blue", title="DirectionalScalper")
       
        table.add_column("Symbol", style="cyan", min_width=12)
        table.add_column("Min. Qty")
        table.add_column("Price")
        table.add_column("1m Vol")
        table.add_column("5m Spread")
        table.add_column("Trend",style="magenta")
        table.add_column("Long Pos. Qty")
        table.add_column("Short Pos. Qty")
        table.add_column("Long uPNL")
        table.add_column("Short uPNL")
        table.add_column("Long cum. uPNL")
        table.add_column("Short cum. uPNL")
        table.add_column("Long Pos. Price")
        table.add_column("Short Pos. Price")

        # Assuming all symbols have the same balance and available balance
        # So, we just pick the last symbol to get these values
        last_symbol_data = list(shared_symbols_data.values())[-1] if shared_symbols_data else None
        if last_symbol_data:
            balance = str(last_symbol_data.get('balance', 0))
            available_bal = str(last_symbol_data.get('available_bal', 0))
            table.caption = f"Balance: {balance}, Available Balance: {available_bal}"

        # Sorting symbols
        sorted_symbols = sorted(shared_symbols_data.values(), key=lambda x: (
            -(x.get('long_pos_qty', 0) > 0 or x.get('short_pos_qty', 0) > 0),  # Prioritize symbols with quantities > 0
            x['symbol']  # Then sort by symbol name
        ))
        
        for symbol_data in sorted_symbols:
            long_pos_qty = symbol_data.get('long_pos_qty', 0)
            short_pos_qty = symbol_data.get('short_pos_qty', 0)
            long_upnl = symbol_data.get('long_upnl', 0)
            short_upnl = symbol_data.get('short_upnl', 0)

            # Determine if the entire row should be bold
            is_bold_row = long_pos_qty > 0 or short_pos_qty > 0

            # Helper function to format the cell
            def format_cell(value, is_bold=is_bold_row, is_highlight=False):
                if is_bold:
                    return f"[b]{value}[/b]"
                elif is_highlight:
                    return f"[b]{value}[/b]" if value > 0 else str(value)
                return str(value)

            row = [
                format_cell(symbol_data['symbol']),
                format_cell(symbol_data.get('min_qty', 0)),
                format_cell(symbol_data.get('current_price', 0)),
                format_cell(symbol_data.get('volume', 0)),
                format_cell(symbol_data.get('spread', 0)),
                format_cell(symbol_data.get('trend', '')),
                format_cell(long_pos_qty),
                format_cell(short_pos_qty),
                format_cell(long_upnl, is_highlight=True),
                format_cell(short_upnl, is_highlight=True),
                format_cell(symbol_data.get('long_cum_pnl', 0)),
                format_cell(symbol_data.get('short_cum_pnl', 0)),
                format_cell(symbol_data.get('long_pos_price', 0)),
                format_cell(symbol_data.get('short_pos_price', 0))
            ]
            table.add_row(*row)

        return table

    def display_table(self):
        console = Console()
        with Live(self.table, refresh_per_second=1/3) as live:
            while True:
                time.sleep(3)
                with self.lock:
                    live.update(self.generate_table())
