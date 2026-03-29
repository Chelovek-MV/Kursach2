"""
Панель навигации
Дерево с разделами: Справочники, Документы, Отчеты
"""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class NavigationPanel(QTreeWidget):
    """Панель навигации с деревом разделов"""
    
    # Сигнал при выборе пункта меню (раздел, пункт)
    item_selected = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(False)
        
        self._setup_navigation()
        self._connect_signals()
        
    def _setup_navigation(self):
        """Создание структуры навигации"""
        
        # Шрифт для заголовков разделов
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(11)
        
        # Раздел "Справочники"
        self.catalogs_section = QTreeWidgetItem(self, ["Справочники"])
        self.catalogs_section.setFont(0, header_font)
        self.catalogs_section.setExpanded(True)
        
        catalog_items = [
            ("products", "Товары"),
            ("brands", "Бренды"),
            ("categories", "Категории"),
            ("customers", "Клиенты"),
            ("suppliers", "Поставщики"),
            ("warehouses", "Склады"),
        ]
        
        for item_id, item_name in catalog_items:
            item = QTreeWidgetItem(self.catalogs_section, [item_name])
            item.setData(0, 100, ("catalog", item_id))  # Сохраняем данные
        
        # Раздел "Документы"
        self.documents_section = QTreeWidgetItem(self, ["Документы"])
        self.documents_section.setFont(0, header_font)
        self.documents_section.setExpanded(True)
        
        document_items = [
            ("orders", "Заказы клиентов"),
            ("purchase_orders", "Закупки"),
            ("stocks", "Остатки на складах"),
        ]
        
        for item_id, item_name in document_items:
            item = QTreeWidgetItem(self.documents_section, [item_name])
            item.setData(0, 100, ("document", item_id))
        
        # Раздел "Отчеты" (основной фокус)
        self.reports_section = QTreeWidgetItem(self, ["Отчеты"])
        self.reports_section.setFont(0, header_font)
        self.reports_section.setExpanded(True)
        
        report_items = [
            ("stock_report", "Остатки товаров"),
            ("sales_report", "Продажи"),
            ("profit_report", "Прибыльность"),
            ("movement_report", "Движение товаров"),
        ]
        
        for item_id, item_name in report_items:
            item = QTreeWidgetItem(self.reports_section, [item_name])
            item.setData(0, 100, ("report", item_id))
    
    def _connect_signals(self):
        """Подключение сигналов"""
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_clicked)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Обработка клика по элементу"""
        data = item.data(0, 100)
        
        if data:
            section, item_id = data
            self.item_selected.emit(section, item_id)
        else:
            # Клик по заголовку раздела - раскрыть/свернуть
            item.setExpanded(not item.isExpanded())
    
    def select_item(self, section: str, item_id: str):
        """Программный выбор элемента"""
        sections = {
            "catalog": self.catalogs_section,
            "document": self.documents_section,
            "report": self.reports_section,
        }
        
        parent = sections.get(section)
        if not parent:
            return
        
        for i in range(parent.childCount()):
            child = parent.child(i)
            data = child.data(0, 100)
            if data and data[1] == item_id:
                self.setCurrentItem(child)
                break
