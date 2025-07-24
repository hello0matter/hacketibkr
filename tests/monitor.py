import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import queue
from datetime import datetime
import sqlite3

from ibapi.client import EClient, Contract, Order
from ibapi.wrapper import EWrapper
from ibapi.common import TickerId

# --- 数据库管理模块 (无需修改) ---
class DatabaseManager:
    # ... (与上一版完全相同) ...
    def __init__(self, db_name="trading_tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            expiry TEXT,
            strike REAL,
            right TEXT,
            quantity INTEGER,
            condition_price REAL,
            stop_price REAL,
            trailing_amount REAL,
            limit_offset REAL,
            limit_price REAL
        )
        """)
        self.conn.commit()

    def add_task(self, task_data):
        columns = ', '.join(task_data.keys())
        placeholders = ', '.join('?' * len(task_data))
        sql = f"INSERT INTO tasks ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(task_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_task(self, task_id, task_data):
        set_clause = ', '.join([f"{key} = ?" for key in task_data.keys()])
        sql = f"UPDATE tasks SET {set_clause} WHERE id = ?"
        self.cursor.execute(sql, tuple(task_data.values()) + (task_id,))
        self.conn.commit()

    def get_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append(dict(zip([c[0] for c in self.cursor.description], row)))
        return tasks

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

# --- IB API 通信核心类 (place_trail_limit_order 已修改) ---
class MyTWSApp(EClient, EWrapper):
    def __init__(self, gui_queue):
        EClient.__init__(self, self)
        self.gui_queue = gui_queue
        self.nextOrderId = -1
        self.next_req_id = 100
        self.tasks = {}
        self.live_quote_req_id = 99

    # ... (大部分方法与上一版相同) ...
    def get_new_req_id(self):
        req_id = self.next_req_id; self.next_req_id += 1; return req_id

    def log(self, message, req_id=None):
        prefix = f"[任务ID:{req_id}] " if req_id else ""
        self.gui_queue.put(("log", f"{prefix}{message}"))

    def update_gui(self, event_type, data):
        self.gui_queue.put((event_type, data))

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        self.log(f"【成功】收到下一个有效订单ID: {orderId}")

    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        super().error(reqId, errorTime, errorCode, errorString, advancedOrderRejectJson)
        if errorCode in [2103, 2104, 2106, 2107, 2157, 2158, 162, 300, 2105, 2150]: return
        id_str = f"请求ID: {reqId}" if reqId != -1 else "系统通知"
        self.log(f"【错误】{id_str}, 错误码: {errorCode}, 消息: {errorString}", req_id=reqId if reqId > 0 else None)
        if reqId in self.tasks and self.tasks[reqId].get('status') not in ["Filled", "Cancelled"]:
            self.update_gui("task_status", {"req_id": reqId, "status": "错误"})

    def tickPrice(self, reqId, field, price, attrib):
        super().tickPrice(reqId, field, price, attrib)

        if reqId == self.live_quote_req_id:
            self.update_gui("live_quote_update", {"field": field, "price": price})
            return

        if reqId in self.tasks:
            task = self.tasks[reqId]
            if field == 1: task['bid'] = price
            elif field == 2: task['ask'] = price

            if task.get('bid', 0) > 0 and task.get('ask', 0) > 0:
                midpoint = (task['bid'] + task['ask']) / 2
                self.update_gui("price_update", {"req_id": reqId, "bid": task['bid'], "ask": task['ask'], "midpoint": midpoint})

                if task.get('is_snapshot'):
                    self.cancelMktData(reqId)
                    self.update_gui("snapshot_done", {"req_id": reqId})
                elif task.get('logic_running') and not task.get('order_placed') and 'params' in task:
                    action = task['params']['action']; condition_price = task['params']['condition_price']
                    if (action == "BUY" and midpoint <= condition_price) or \
                            (action == "SELL" and midpoint >= condition_price):
                        self.log(f"*** 本地条件满足！中点价 {midpoint:.2f} 已达到监控价 {condition_price}。正在提交TRAIL LIMIT订单... ***", req_id=reqId)
                        self.place_trail_limit_order(reqId)
                        self.stop_trade_logic(reqId, from_order=True, keep_price_feed=True)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        for req_id, task in self.tasks.items():
            if task.get('orderId') == orderId:
                self.log(f"订单状态: {status}, 成交: {filled}, 剩余: {remaining}, 均价: {avgFillPrice:.2f}", req_id=req_id)
                self.update_gui("task_status", {"req_id": req_id, "status": status})
                if status in ["Filled", "Cancelled", "Inactive"]: self.stop_trade_logic(req_id, from_order=True)
                break

    def add_task(self, db_id, task_data):
        req_id = self.get_new_req_id()
        self.tasks[req_id] = {"db_id": db_id, "params": task_data, "status": "待命", "logic_running": False}
        return req_id

    def get_price(self, req_id, contract, is_snapshot=False):
        if req_id == self.live_quote_req_id:
            self.cancelMktData(self.live_quote_req_id)
            self.reqMktData(req_id, contract, "", False, False, [])
            return

        if req_id in self.tasks and self.tasks[req_id].get('status') not in ["获取报价中", "监控中"]:
            self.tasks[req_id].update({"is_snapshot": is_snapshot, "status": "获取报价中"})
            self.update_gui("task_status", {"req_id": req_id, "status": "获取报价中"})
            self.log("正在请求市场数据...", req_id=req_id)
            self.reqMktData(req_id, contract, "", is_snapshot, False, [])

    def start_trade_logic(self, req_id):
        if req_id in self.tasks and not self.tasks[req_id].get('logic_running'):
            task = self.tasks[req_id]
            task['logic_running'] = True; task['order_placed'] = False
            self.log("本地监控已启动，等待价格触及监控价...", req_id=req_id)
            self.update_gui("task_status", {"req_id": req_id, "status": "监控中"})
            if 'bid' not in task: self.get_price(req_id, self._create_contract_from_task(task))

    def stop_trade_logic(self, req_id, from_order=False, keep_price_feed=False):
        if req_id in self.tasks:
            task = self.tasks[req_id]
            if task.get('logic_running'):
                task['logic_running'] = False
                if task.get('orderId') and not from_order:
                    self.log("正在取消已提交的订单...", req_id=req_id); self.cancelOrder(task['orderId'], "")
                elif not from_order:
                    self.log("交易逻辑已手动停止。"); self.update_gui("task_status", {"req_id": req_id, "status": "已停止"})
            if not keep_price_feed: self.cancelMktData(req_id)

    def place_trail_limit_order(self, req_id):
        """
        修正后的下单逻辑，严格遵循TRAIL LIMIT订单的参数要求。
        """
        task = self.tasks[req_id]
        if task.get('order_placed'): return
        self.log(f"正在为 {task['params']['quantity']} 份合约提交TRAIL LIMIT订单...", req_id=req_id)
        order = Order(); order.action = task['params']['action']; order.orderType = "TRAIL LIMIT"
        order.totalQuantity = task['params']['quantity']

        # *** 关键修改：严格设置订单参数 ***
        order.trailStopPrice = task['params']['stop_price']     # 追踪起始价
        order.auxPrice = task['params']['trailing_amount']  # 追踪金额 (不是auxPrice)

        # 必须设置 lmtPrice 或 lmtPriceOffset (auxPrice)
        if task['params']['limit_price'] is not None:
            order.lmtPrice = task['params']['limit_price']
        else:
            order.lmtPriceOffset = task['params']['limit_offset'] # 使用限价偏移

        order.tif = "GTC"; order.outsideRth = True

        task['orderId'] = self.nextOrderId
        self.placeOrder(self.nextOrderId, self._create_contract_from_task(task), order)
        task['order_placed'] = True
        self.update_gui("task_status", {"req_id": req_id, "status": "已提交"})
        self.nextOrderId += 1

    def _create_contract_from_task(self, task):
        params = task['params']; contract = Contract()
        contract.symbol = params['symbol']; contract.secType = "STK" if params['asset_type'] == "股票" else "OPT"
        contract.exchange = "SMART"; contract.currency = "USD"
        if contract.secType == "OPT":
            contract.lastTradeDateOrContractMonth = params['expiry']
            contract.strike = params['strike']; contract.right = params['right']; contract.multiplier = "100"
        return contract

# --- GUI 应用类 (完整最终版) ---
class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IBKR 双向条件追踪交易平台 (v13 - AutoQuote)")
        # ... (与上一版相同) ...
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.db = DatabaseManager()
        self.gui_queue = queue.Queue()
        self.api_thread = None; self.ib_app = None; self.task_map = {}
        self.live_quote_data = {}
        self.create_widgets()
        self.process_gui_queue()

    def create_widgets(self):
        # ... (主框架和连接控制) ...
        main_frame = ttk.Frame(self.root, padding="10"); main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1); self.root.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame, padding="10"); left_frame.grid(row=0, column=0, sticky="ns")

        conn_frame = ttk.LabelFrame(left_frame, text="连接控制"); conn_frame.pack(fill="x", pady=5)
        self.connect_button = ttk.Button(conn_frame, text="连接", command=self.connect_to_tws); self.connect_button.pack(side="left", padx=5)
        self.disconnect_button = ttk.Button(conn_frame, text="断开", command=self.disconnect_from_tws, state="disabled"); self.disconnect_button.pack(side="left", padx=5)

        live_quote_frame = ttk.LabelFrame(left_frame, text="实时价格观察"); live_quote_frame.pack(fill="x", pady=5)
        self.live_quote_label = ttk.Label(live_quote_frame, text="请从下方选择蓝筹股...", font=("Segoe UI", 10, "bold"))
        self.live_quote_label.pack(pady=5)

        stock_frame = ttk.LabelFrame(left_frame, text="添加股票任务"); stock_frame.pack(fill="x", pady=5)
        ttk.Label(stock_frame, text="选择蓝筹股:").pack(anchor="w")
        self.watchlist = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "WMT", "LLY", "V", "COST"]
        self.stock_var = tk.StringVar()
        stock_menu = ttk.Combobox(stock_frame, textvariable=self.stock_var, values=self.watchlist, state="readonly"); stock_menu.pack(fill="x", pady=2)
        stock_menu.bind("<<ComboboxSelected>>", self.on_stock_select)

        self.stock_entries = self.create_param_fields(stock_frame, ["方向", "股票代码", "数量", "监控触发价", "止损价", "追踪金额", "最高限价(可选)", "限价偏移"])
        ttk.Button(stock_frame, text="添加股票到列表", command=lambda: self.add_task_to_list("股票")).pack(pady=10)

        option_frame = ttk.LabelFrame(left_frame, text="添加期权任务"); option_frame.pack(fill="x", pady=5)
        self.option_entries = self.create_param_fields(option_frame, ["方向", "股票代码", "到期日(YYYYMMDD)", "行权价", "类型(C/P)", "数量", "监控触发价", "止损价", "追踪金额", "最高限价(可选)", "限价偏移"])
        for key in ["到期日(YYYYMMDD)", "行权价", "类型(C/P)"]: self.option_entries[key].bind("<FocusOut>", self.on_option_param_change)
        ttk.Button(option_frame, text="添加期权到列表", command=lambda: self.add_task_to_list("期权")).pack(pady=10)

        right_frame = ttk.Frame(main_frame); right_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.columnconfigure(1, weight=1); main_frame.rowconfigure(0, weight=1)

        task_list_frame = ttk.LabelFrame(right_frame, text="监控列表"); task_list_frame.pack(fill="both", expand=True, pady=5, padx=5)
        cols = ("ID", "方向", "合约", "买价", "卖价", "中点价", "状态"); self.tree = ttk.Treeview(task_list_frame, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col); self.tree.column(col, width=80, anchor="center")
        self.tree.column("合约", width=180); self.tree.pack(side="left", fill="both", expand=True); self.tree.bind("<Double-1>", self.open_edit_window)

        action_panel = ttk.Frame(task_list_frame); action_panel.pack(side="left", fill="y", padx=5)
        ttk.Label(action_panel, text="操作").pack()
        # *** 关键修改：移除“获取报价”按钮 ***
        ttk.Button(action_panel, text="启动逻辑", command=lambda: self.control_task("start_logic")).pack(fill="x", pady=2)
        ttk.Button(action_panel, text="停止逻辑", command=lambda: self.control_task("stop_logic")).pack(fill="x", pady=2)
        ttk.Button(action_panel, text="移除任务", command=lambda: self.control_task("remove")).pack(fill="x", pady=2)

        log_frame = ttk.LabelFrame(right_frame, text="日志"); log_frame.pack(fill="both", expand=True, pady=5, padx=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10); self.log_text.pack(fill="both", expand=True)

    def create_param_fields(self, parent, labels):
        # ... (与上一版相同) ...
        entries = {}; defaults = {"数量": "1", "追踪金额": "1.0", "限价偏移": "0.01", "类型(C/P)": "C"}
        for label in labels:
            frame = ttk.Frame(parent); frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=f"{label}:", width=15).pack(side="left")
            if label == "方向":
                combo = ttk.Combobox(frame, values=["BUY", "SELL"], state="readonly")
                combo.pack(side="left", fill="x", expand=True)
                combo.set("BUY")
                entries[label] = combo
            else:
                entry = ttk.Entry(frame); entry.pack(side="left", fill="x", expand=True)
                if label in defaults: entry.insert(0, defaults[label])
                entries[label.replace("(可选)", "")] = entry
        return entries

    def add_task_to_list(self, asset_type):
        # ... (与上一版相同) ...
        entries = self.stock_entries if asset_type == "股票" else self.option_entries
        try:
            if asset_type == "股票":
                task_data = {
                    "action": entries["方向"].get(), "asset_type": "股票", "symbol": entries["股票代码"].get().upper(),
                    "quantity": int(entries["数量"].get()), "condition_price": float(entries["监控触发价"].get()),
                    "stop_price": float(entries["止损价"].get()), "trailing_amount": float(entries["追踪金额"].get()),
                    "limit_offset": float(entries["限价偏移"].get()), "limit_price": float(val) if (val := entries["最高限价"].get()) else None,
                    "expiry": None, "strike": None, "right": None
                }
            else:
                task_data = {
                    "action": entries["方向"].get(), "asset_type": "期权", "symbol": entries["股票代码"].get().upper(),
                    "quantity": int(entries["数量"].get()), "condition_price": float(entries["监控触发价"].get()),
                    "stop_price": float(entries["止损价"].get()), "trailing_amount": float(entries["追踪金额"].get()),
                    "limit_offset": float(entries["限价偏移"].get()), "limit_price": float(val) if (val := entries["最高限价"].get()) else None,
                    "expiry": entries["到期日(YYYYMMDD)"].get(), "strike": float(entries["行权价"].get()), "right": entries["类型(C/P)"].get().upper()
                }

            if not task_data['symbol']: raise ValueError("股票代码不能为空")
            db_id = self.db.add_task(task_data)
            self.load_task_to_treeview(db_id, task_data)
        except (ValueError, KeyError) as e:
            messagebox.showerror("输入错误", f"请检查参数是否正确填写: {e}")

    def open_edit_window(self, event):
        # ... (与上一版相同) ...
        selected_item = self.tree.focus();
        if not selected_item: return
        req_id = int(selected_item)
        task = self.ib_app.tasks.get(req_id);
        if not task: return

        edit_win = tk.Toplevel(self.root); edit_win.title(f"编辑任务 (DB ID: {task['db_id']})")

        asset_type = task['params']['asset_type']
        labels = ["方向", "股票代码", "数量", "监控触发价", "止损价", "追踪金额", "最高限价(可选)", "限价偏移"]
        if asset_type == "期权":
            labels.insert(2, "类型(C/P)"); labels.insert(2, "行权价"); labels.insert(2, "到期日(YYYYMMDD)")

        edit_entries = self.create_param_fields(edit_win, labels)

        key_map = {
            "方向": "action", "股票代码": "symbol", "数量": "quantity", "监控触发价": "condition_price", "止损价": "stop_price",
            "追踪金额": "trailing_amount", "最高限价": "limit_price", "限价偏移": "limit_offset",
            "到期日(YYYYMMDD)": "expiry", "行权价": "strike", "类型(C/P)": "right"
        }

        for label, widget in edit_entries.items():
            db_key = key_map.get(label.replace("(可选)", ""))
            if db_key and db_key in task['params'] and task['params'][db_key] is not None:
                if isinstance(widget, ttk.Combobox):
                    widget.set(str(task['params'][db_key]))
                else:
                    widget.delete(0, 'end'); widget.insert(0, str(task['params'][db_key]))

        def save_changes():
            try:
                new_params = {}
                for label, widget in edit_entries.items():
                    db_key = key_map.get(label.replace("(可选)", ""))
                    if db_key:
                        value = widget.get()
                        if db_key in ['quantity']: value = int(value) if value else None
                        elif db_key in ['strike', 'condition_price', 'stop_price', 'trailing_amount', 'limit_offset', 'limit_price']:
                            value = float(value) if value else None
                        if db_key in ['expiry', 'right'] and not value: value = None
                        new_params[db_key] = value

                new_params['asset_type'] = asset_type
                self.db.update_task(task['db_id'], new_params)
                self.ib_app.tasks[req_id]['params'] = new_params
                self.tree.set(req_id, "方向", new_params['action'])
                messagebox.showinfo("成功", "任务修改已保存！", parent=edit_win)
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}", parent=edit_win)

        ttk.Button(edit_win, text="保存修改", command=save_changes).pack(pady=10)

    def process_gui_queue(self):
        try:
            while True:
                event_type, data = self.gui_queue.get_nowait()
                if event_type == "log":
                    self.log_text.insert(tk.END, data + "\n"); self.log_text.see(tk.END)
                elif event_type == "task_status":
                    if self.tree.exists(data['req_id']): self.tree.set(data['req_id'], "状态", data['status'])
                elif event_type == "price_update":
                    # *** 关键修改：现在这个事件只更新列表中的价格 ***
                    req_id = data['req_id']
                    if self.tree.exists(req_id):
                        self.tree.set(req_id, "买价", f"{data['bid']:.2f}")
                        self.tree.set(req_id, "卖价", f"{data['ask']:.2f}")
                        self.tree.set(req_id, "中点价", f"{data['midpoint']:.2f}")
                elif event_type == "live_quote_update":
                    field, price = data['field'], data['price']
                    if field == 1: self.live_quote_data['bid'] = price
                    elif field == 2: self.live_quote_data['ask'] = price
                    bid = self.live_quote_data.get('bid', 0); ask = self.live_quote_data.get('ask', 0)
                    if bid > 0 and ask > 0:
                        self.live_quote_label.config(text=f"买: {bid:.2f} | 卖: {ask:.2f} | 中: {(bid+ask)/2:.2f}")

                elif event_type == "snapshot_done":
                    req_id = data['req_id']; task_info = self.ib_app.tasks.get(req_id)
                    if task_info:
                        entries = self.stock_entries if task_info['asset_type'] == "股票" else self.option_entries
                        midpoint = (task_info.get('bid', 0) + task_info.get('ask', 0)) / 2
                        if midpoint > 0:
                            entries["监控触发价"].delete(0, 'end'); entries["监控触发价"].insert(0, f"{midpoint * 0.99:.2f}")
                            entries["止损价"].delete(0, 'end'); entries["止损价"].insert(0, f"{midpoint * 0.98:.2f}")
                        if req_id in self.ib_app.tasks: del self.ib_app.tasks[req_id]
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_gui_queue)

    def on_stock_select(self, event=None):
        symbol = self.stock_var.get();
        if not symbol or not self.ib_app or not self.ib_app.isConnected(): return
        self.stock_entries["股票代码"].delete(0, 'end'); self.stock_entries["股票代码"].insert(0, symbol)
        self.option_entries["股票代码"].delete(0, 'end'); self.option_entries["股票代码"].insert(0, symbol)

        # 请求独立的实时报价
        self.live_quote_data.clear()
        self.live_quote_label.config(text=f"正在获取 {symbol} 报价...")
        contract = Contract(); contract.symbol = symbol; contract.secType = "STK"; contract.exchange = "SMART"; contract.currency = "USD"
        self.ib_app.get_price(self.ib_app.live_quote_req_id, contract)

    def on_option_param_change(self, event=None):
        """
        当期权参数输入框失去焦点时触发，尝试获取期权的实时报价。
        """
        if not self.ib_app or not self.ib_app.isConnected(): return

        try:
            # 尝试从UI构建期权合约，如果任何参数为空或无效，会触发异常
            contract = self.build_contract_from_entries(self.option_entries, "期权")

            # 如果所有参数都有效，则发起实时报价请求
            self.live_quote_data.clear()
            contract_desc = f"{contract.symbol} {contract.lastTradeDateOrContractMonth[2:]}{contract.right}{contract.strike}"
            self.live_quote_label.config(text=f"正在获取 {contract_desc} 报价...")
            self.ib_app.get_price(self.ib_app.live_quote_req_id, contract)

        except (ValueError, KeyError, tk.TclError):
            # 如果参数不完整（例如，行权价还没填），或者输入格式错误，
            # build_contract_from_entries会失败，我们在这里静默捕获异常，不执行任何操作。
            # 这可以防止在用户输入过程中频繁报错。
            self.live_quote_label.config(text="请填写完整的期权参数...")
            pass

    def get_snapshot_quote(self, entries, asset_type="股票"):
        if not self.ib_app or not self.ib_app.isConnected(): return
        try:
            contract = self.build_contract_from_entries(entries, asset_type)
            req_id = self.ib_app.get_new_req_id()
            self.ib_app.tasks[req_id] = {"status": "快照中", "asset_type": asset_type}
            self.ib_app.get_price(req_id, contract, is_snapshot=True)
        except (ValueError, KeyError):
            pass

    def load_task_to_treeview(self, db_id, task_data):
        """
        修正后的加载逻辑，会自动为新任务获取持续报价。
        """
        if self.ib_app and self.ib_app.isConnected():
            req_id = self.ib_app.add_task(db_id, task_data)
            self.task_map[db_id] = req_id
            contract_desc = f"{task_data['symbol']} STK"
            if task_data['asset_type'] == "期权":
                contract_desc = f"{task_data['symbol']} {task_data['expiry'][2:]}{task_data['right']}{task_data['strike']}"

            self.tree.insert("", "end", iid=req_id, values=(db_id, task_data['action'], contract_desc, "-", "-", "-", "待命"))

            # *** 关键修改：自动获取持续报价 ***
            contract = self.ib_app._create_contract_from_task(self.ib_app.tasks[req_id])
            self.ib_app.get_price(req_id, contract)
        else:
            messagebox.showwarning("警告", "请先连接到TWS以激活任务。")

    def load_all_tasks_from_db(self):
        tasks = self.db.get_all_tasks()
        for task in tasks: self.load_task_to_treeview(task['id'], task)

    def control_task(self, action):
        selected_item = self.tree.focus()
        if not selected_item: messagebox.showwarning("提示", "请先在列表中选择一个任务。"); return
        req_id = int(selected_item)

        # *** 关键修改：移除 get_price 逻辑，因为它现在是自动的 ***
        if action == "start_logic": self.ib_app.start_trade_logic(req_id)
        elif action == "stop_logic": self.ib_app.stop_trade_logic(req_id)
        elif action == "remove":
            db_id = self.ib_app.tasks[req_id]['db_id']
            self.ib_app.stop_trade_logic(req_id) # 先停止逻辑和数据流
            self.tree.delete(selected_item)
            del self.ib_app.tasks[req_id]; del self.task_map[db_id]
            self.db.delete_task(db_id)
            self.log_text.insert(tk.END, f"【操作】已移除并从数据库删除任务 (DB_ID: {db_id})\n")

    def connect_to_tws(self):
        # ... (与上一版相同) ...
        if self.ib_app and self.ib_app.isConnected(): return
        self.ib_app = MyTWSApp(self.gui_queue)
        try:
            port = 7496; client_id = int(time.time() % 1000)
            self.ib_app.connect("127.0.0.1", port, clientId=client_id)
            self.log_text.insert(tk.END, f"【操作】正在连接到 TWS/IB Gateway, 端口: {port}, 客户端ID: {client_id}...\n")
            self.api_thread = threading.Thread(target=self.ib_app.run, daemon=True); self.api_thread.start()
            time.sleep(1)
            self.connect_button.config(state="disabled"); self.disconnect_button.config(state="normal")
            self.load_all_tasks_from_db()
        except Exception as e:
            self.log_text.insert(tk.END, f"【错误】连接失败: {e}\n"); self.ib_app = None

    def disconnect_from_tws(self):
        # ... (与上一版相同) ...
        if self.ib_app and self.ib_app.isConnected(): self.ib_app.disconnect(); self.log_text.insert(tk.END, "【操作】已手动断开连接。\n")
        self.connect_button.config(state="normal"); self.disconnect_button.config(state="disabled")
        self.ib_app = None; self.api_thread = None
        for i in self.tree.get_children(): self.tree.delete(i)
        self.task_map.clear()
        self.live_quote_label.config(text="请从下方选择蓝筹股...")
        self.live_quote_data.clear()

    def build_contract_from_entries(self, entries, asset_type):
        # ... (与上一版相同) ...
        contract = Contract(); contract.symbol = entries["股票代码"].get().upper()
        contract.secType = "STK" if asset_type == "股票" else "OPT"; contract.exchange = "SMART"; contract.currency = "USD"
        if contract.secType == "OPT":
            contract.lastTradeDateOrContractMonth = entries["到期日(YYYYMMDD)"].get()
            contract.strike = float(entries["行权价"].get()); contract.right = entries["类型(C/P)"].get().upper()
        return contract

    def on_closing(self):
        self.db.close()
        self.disconnect_from_tws()
        self.root.destroy()

if __name__ == "__main__":
    # 第一次运行时，如果 trading_tasks.db 存在旧结构，请手动删除它
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()

