"""
Отчет "Остатки товаров"
Показывает текущие остатки товаров на складах
"""

from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtCore import QDate
from sqlalchemy import func

import sys
sys.path.append('..')
from models import Product, Brand, Category, Warehouse, Stock
from .base_report import BaseReportWidget


class StockReportWidget(BaseReportWidget):
    """Отчет по остаткам товаров"""
    
    def __init__(self, session, parent=None):
        self.report_title = "Остатки товаров"
        super().__init__(session, parent)
    
    def _setup_filters(self):
        """Настройка фильтров"""
        
        # Первая строка: Склад, Категория
        row1 = QHBoxLayout()
        
        # Склад
        warehouses = [(w.id, w.name) for w in self.session.query(Warehouse).all()]
        self.filter_warehouse = self.create_combo_filter(warehouses)
        row1.addWidget(self._create_label("Склад:"))
        row1.addWidget(self.filter_warehouse)
        
        row1.addSpacing(20)
        
        # Категория
        categories = [(c.id, c.name) for c in self.session.query(Category).all()]
        self.filter_category = self.create_combo_filter(categories)
        row1.addWidget(self._create_label("Категория:"))
        row1.addWidget(self.filter_category)
        
        row1.addStretch()
        self.filter_layout.addLayout(row1)
        
        # Вторая строка: Бренд, Чекбоксы
        row2 = QHBoxLayout()
        
        # Бренд
        brands = [(b.id, b.name) for b in self.session.query(Brand).all()]
        self.filter_brand = self.create_combo_filter(brands)
        row2.addWidget(self._create_label("Бренд:"))
        row2.addWidget(self.filter_brand)
        
        row2.addSpacing(20)
        
        # Чекбоксы
        self.filter_only_available = self.create_checkbox_filter("Только с остатками", True)
        row2.addWidget(self.filter_only_available)
        
        row2.addSpacing(20)
        
        self.filter_below_min = self.create_checkbox_filter("Ниже минимума")
        row2.addWidget(self.filter_below_min)
        
        row2.addStretch()
        self.filter_layout.addLayout(row2)
    
    def _create_label(self, text):
        """Создать метку"""
        from PyQt6.QtWidgets import QLabel
        label = QLabel(text)
        label.setMinimumWidth(80)
        return label
    
    def generate_report(self):
        """Формирование отчета"""
        try:
            # Базовый запрос
            query = self.session.query(
                Product.articul,
                Product.name.label('product_name'),
                Brand.name.label('brand_name'),
                Category.name.label('category_name'),
                Warehouse.name.label('warehouse_name'),
                Stock.quantity,
                Product.min_balance
            ).outerjoin(
                Stock, Stock.product_id == Product.id
            ).outerjoin(
                Warehouse, Warehouse.id == Stock.warehouse_id
            ).outerjoin(
                Brand, Brand.id == Product.brand_id
            ).outerjoin(
                Category, Category.id == Product.category_id
            )
            
            # Применяем фильтры
            warehouse_id = self.filter_warehouse.currentData()
            if warehouse_id:
                query = query.filter(Stock.warehouse_id == warehouse_id)
            
            category_id = self.filter_category.currentData()
            if category_id:
                query = query.filter(Product.category_id == category_id)
            
            brand_id = self.filter_brand.currentData()
            if brand_id:
                query = query.filter(Product.brand_id == brand_id)
            
            if self.filter_only_available.isChecked():
                query = query.filter(Stock.quantity > 0)
            
            if self.filter_below_min.isChecked():
                query = query.filter(Stock.quantity < Product.min_balance)
            
            # Выполняем запрос
            results = query.all()
            
            # Формируем данные для таблицы
            headers = [
                "Артикул", "Наименование", "Бренд", "Категория",
                "Склад", "Остаток", "Мин. остаток"
            ]
            
            data = []
            total_quantity = 0
            
            for row in results:
                quantity = row.quantity or 0
                total_quantity += quantity
                
                data.append([
                    row.articul or "",
                    row.product_name or "",
                    row.brand_name or "",
                    row.category_name or "",
                    row.warehouse_name or "Не указан",
                    quantity,
                    row.min_balance or 0
                ])
            
            # Итоги
            totals = {
                5: total_quantity,  # Сумма остатков
            }
            
            self.display_data(headers, data, totals)
            
            # Панель итогов
            self.clear_totals()
            self.add_total_label("Всего позиций", len(data))
            self.add_total_label("Общий остаток", f"{total_quantity:,}".replace(",", " "))
            
            if self.filter_below_min.isChecked():
                self.add_total_label("Ниже минимума", len(data), "#cc0000")
            
            self.totals_layout.addStretch()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", f"Ошибка формирования отчета: {e}")
