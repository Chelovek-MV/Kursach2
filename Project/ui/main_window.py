"""
Главное окно приложения
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStackedWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QKeySequence
from PyQt6.QtGui import QShortcut

from .styles import MAIN_STYLE
from .navigation_panel import NavigationPanel
from .toolbar import MainToolBar


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, session):
        super().__init__()
        
        self.session = session
        self.current_widget = None
        
        self._setup_window()
        self._setup_menu()
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Показываем приветственный экран
        self._show_welcome()
    
    def _setup_window(self):
        """Настройка окна"""
        self.setWindowTitle("Управление автозапчастями")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 600)
        
        # Применяем стили
        self.setStyleSheet(MAIN_STYLE)
    
    def _setup_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        action_export = QAction("Экспорт в Excel", self)
        action_export.setShortcut(QKeySequence("Ctrl+E"))
        action_export.triggered.connect(self._on_export)
        file_menu.addAction(action_export)
        
        file_menu.addSeparator()
        
        action_exit = QAction("Выход", self)
        action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # Меню "Справочники"
        catalog_menu = menubar.addMenu("Справочники")
        
        catalogs = [
            ("Товары", "products"),
            ("Бренды", "brands"),
            ("Категории", "categories"),
            ("Клиенты", "customers"),
            ("Поставщики", "suppliers"),
            ("Склады", "warehouses"),
        ]
        
        for name, item_id in catalogs:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, i=item_id: self._open_section("catalog", i))
            catalog_menu.addAction(action)
        
        # Меню "Отчеты"
        reports_menu = menubar.addMenu("Отчеты")
        
        reports = [
            ("Остатки товаров", "stock_report"),
            ("Продажи", "sales_report"),
            ("Прибыльность", "profit_report"),
            ("Движение товаров", "movement_report"),
        ]
        
        for name, item_id in reports:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, i=item_id: self._open_section("report", i))
            reports_menu.addAction(action)
        
        # Меню "Помощь"
        help_menu = menubar.addMenu("Помощь")
        
        action_about = QAction("О программе", self)
        action_about.triggered.connect(self._show_about)
        help_menu.addAction(action_about)
    
    def _setup_ui(self):
        """Создание интерфейса"""
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Панель инструментов
        self.toolbar = MainToolBar()
        main_layout.addWidget(self.toolbar)
        
        # Сплиттер для навигации и контента
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Панель навигации (слева)
        self.nav_panel = NavigationPanel()
        self.nav_panel.setMinimumWidth(200)
        self.nav_panel.setMaximumWidth(350)
        self.splitter.addWidget(self.nav_panel)
        
        # Область контента (справа)
        self.content_stack = QStackedWidget()
        self.splitter.addWidget(self.content_stack)
        
        # Пропорции сплиттера
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)
        self.splitter.setSizes([250, 1150])
        
        main_layout.addWidget(self.splitter)
        
        # Статусбар
        self.statusBar().showMessage("Готово")
    
    def _setup_shortcuts(self):
        """Настройка горячих клавиш"""
        sc = QShortcut(QKeySequence("Ctrl+O"), self)
        sc.activated.connect(lambda: self._on_quick_op("sale"))
    
    def _connect_signals(self):
        """Подключение сигналов"""
        
        # Навигация
        self.nav_panel.item_selected.connect(self._open_section)
        
        # Тулбар
        self.toolbar.action_add.connect(self._on_add)
        self.toolbar.action_edit.connect(self._on_edit)
        self.toolbar.action_delete.connect(self._on_delete)
        self.toolbar.action_refresh.connect(self._on_refresh)
        self.toolbar.action_export.connect(self._on_export)
        self.toolbar.action_quick_op.connect(self._on_quick_op)
    
    def _show_welcome(self):
        """Показать приветственный экран"""
        welcome = QWidget()
        layout = QVBoxLayout(welcome)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Заголовок
        title = QLabel("Управление автозапчастями")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #cc0000;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Выберите раздел в панели навигации слева")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666666; margin-top: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Подсказки
        hints = QLabel(
            "\n\nБыстрый доступ:\n"
            "• Справочники - управление товарами, клиентами, поставщиками\n"
            "• Документы - заказы, закупки, остатки\n"
            "• Отчеты - аналитика продаж, остатков, прибыльности"
        )
        hints_font = QFont()
        hints_font.setPointSize(12)
        hints.setFont(hints_font)
        hints.setStyleSheet("color: #888888;")
        hints.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hints)
        
        self.content_stack.addWidget(welcome)
        self.content_stack.setCurrentWidget(welcome)
        
        self.toolbar.set_welcome_mode()
        self.toolbar.set_title("Добро пожаловать")
    
    def _open_section(self, section: str, item_id: str):
        """Открыть раздел"""
        
        # Импортируем виджеты здесь, чтобы избежать циклических импортов
        from .catalog_widget import CatalogWidget
        from reports.stock_report import StockReportWidget
        from reports.sales_report import SalesReportWidget
        from reports.profit_report import ProfitReportWidget
        from reports.movement_report import MovementReportWidget
        
        # Заголовки разделов
        titles = {
            "products": "Справочник: Товары",
            "brands": "Справочник: Бренды",
            "categories": "Справочник: Категории",
            "customers": "Справочник: Клиенты",
            "suppliers": "Справочник: Поставщики",
            "warehouses": "Справочник: Склады",
            "orders": "Документы: Заказы клиентов",
            "purchase_orders": "Документы: Закупки",
            "stocks": "Документы: Остатки на складах",
            "stock_report": "Отчет: Остатки товаров",
            "sales_report": "Отчет: Продажи",
            "profit_report": "Отчет: Прибыльность",
            "movement_report": "Отчет: Движение товаров",
        }
        
        title = titles.get(item_id, item_id)
        self.toolbar.set_title(title)
        
        # Создаем виджет в зависимости от типа раздела
        if section == "catalog":
            widget = CatalogWidget(self.session, item_id)
            self.toolbar.set_catalog_mode()
        elif section == "document":
            widget = CatalogWidget(self.session, item_id)
            self.toolbar.set_catalog_mode()
        elif section == "report":
            if item_id == "stock_report":
                widget = StockReportWidget(self.session)
            elif item_id == "sales_report":
                widget = SalesReportWidget(self.session)
            elif item_id == "profit_report":
                widget = ProfitReportWidget(self.session)
            elif item_id == "movement_report":
                widget = MovementReportWidget(self.session)
            else:
                return
            self.toolbar.set_report_mode()
        else:
            return
        
        # Удаляем старый виджет и добавляем новый
        if self.current_widget:
            self.content_stack.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
        
        self.current_widget = widget
        self.content_stack.addWidget(widget)
        self.content_stack.setCurrentWidget(widget)
        
        self.statusBar().showMessage(f"Открыт раздел: {title}")
    
    def _on_quick_op(self, operation_type: str = "sale"):
        """Открыть диалог быстрого создания операции"""
        from .dialogs.quick_operation_dialog import QuickOperationDialog

        op_labels = {
            "sale":     "Продажа",
            "purchase": "Закупка",
            "move":     "Перемещение",
            "receipt":  "Приход",
            "writeoff": "Списание",
        }

        dialog = QuickOperationDialog(self.session, operation_type, self)
        if dialog.exec():
            label = op_labels.get(operation_type, operation_type)
            self.statusBar().showMessage(f"Операция «{label}» успешно проведена")
            # Обновляем текущий виджет, если он открыт
            if self.current_widget and hasattr(self.current_widget, 'refresh_data'):
                self.current_widget.refresh_data()

    def _on_add(self):
        """Добавить запись"""
        if self.current_widget and hasattr(self.current_widget, 'add_record'):
            self.current_widget.add_record()
    
    def _on_edit(self):
        """Редактировать запись"""
        if self.current_widget and hasattr(self.current_widget, 'edit_record'):
            self.current_widget.edit_record()
    
    def _on_delete(self):
        """Удалить запись"""
        if self.current_widget and hasattr(self.current_widget, 'delete_record'):
            self.current_widget.delete_record()
    
    def _on_refresh(self):
        """Обновить данные"""
        if self.current_widget and hasattr(self.current_widget, 'refresh_data'):
            self.current_widget.refresh_data()
            self.statusBar().showMessage("Данные обновлены")
    
    def _on_export(self):
        """Экспорт в Excel"""
        if self.current_widget and hasattr(self.current_widget, 'export_to_excel'):
            self.current_widget.export_to_excel()
    
    def _show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>Управление автозапчастями</h2>"
            "<p>Версия 1.0</p>"
            "<p>Система учета и управления магазином автозапчастей</p>"
        )
