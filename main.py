import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QMessageBox, QComboBox, QScrollArea,
                            QSizePolicy, QHeaderView, QCalendarWidget,
                            QToolButton)
from PyQt6.QtCore import Qt, QDate, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')
from database import Database
from analytics import Analytics

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система учета нарядов")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Таймер для отложенного обновления графиков
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.delayed_update_analytics)
        
        self.db = Database()
        self.analytics = Analytics(self.db)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Инициализация вкладок
        self.init_data_tab()
        self.init_analytics_tab()
        
        # Загружаем данные
        self.load_data()

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        # Получаем новый размер окна
        new_size = event.size()
        # Устанавливаем минимальную ширину для scroll area
        scroll_area = self.tabs.widget(1).findChild(QScrollArea)
        if scroll_area:
            scroll_area.setMinimumWidth(new_size.width() - 40)
            content_widget = scroll_area.widget()
            if content_widget:
                content_widget.setMinimumWidth(new_size.width() - 60)
        # Запускаем таймер для отложенного обновления
        self.resize_timer.start(200)

    def delayed_update_analytics(self):
        """Отложенное обновление графиков"""
        # Получаем размер окна
        window_size = self.size()
        # Вычисляем новый размер для графиков (с учетом отступов)
        canvas_width = window_size.width() - 100
        canvas_height = 300
        
        # Обновляем размеры всех canvas и их содержимого
        for canvas in [self.orders_canvas, self.productivity_canvas, 
                      self.complexity_canvas]:
            if canvas:
                # Обновляем размеры canvas
                canvas.setMinimumWidth(canvas_width)
                canvas.setMaximumWidth(canvas_width)
                # Обновляем размеры figure
                canvas.figure.set_size_inches(canvas_width/100, canvas_height/100)
                canvas.figure.tight_layout()
                canvas.draw_idle()
        
        if self.prediction_canvas:
            self.prediction_canvas.setMinimumWidth(canvas_width)
            self.prediction_canvas.setMaximumWidth(canvas_width)
            self.prediction_canvas.figure.set_size_inches(canvas_width/100, canvas_height/100)
            self.prediction_canvas.figure.tight_layout()
            self.prediction_canvas.draw_idle()

    def init_data_tab(self):
        """Инициализация вкладки с данными"""
        data_tab = QWidget()
        layout = QVBoxLayout()
        
        # Форма добавления/редактирования
        form_layout = QHBoxLayout()
        
        # Общий стиль для всех полей ввода
        input_style = """
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 3px;
                min-height: 20px;
            }
            QLineEdit:hover {
                border: 1px solid #5d5d5d;
            }
            QLineEdit:focus {
                border: 1px solid #5d5d5d;
            }
        """
        
        # Создаем и настраиваем все поля ввода
        self.shifr_input = QLineEdit()
        self.date_input = QLineEdit()
        self.workshop_input = QLineEdit()
        self.employee_input = QLineEdit()
        self.operation_input = QLineEdit()
        self.time_norm_input = QLineEdit()
        self.parts_count_input = QLineEdit()

        # Устанавливаем текущую дату и настраиваем все поля
        self.date_input.setText(QDate.currentDate().toString("dd.MM.yyyy"))
        
        # Применяем стиль и выравнивание ко всем полям
        for input_field in [self.shifr_input, self.date_input, self.workshop_input,
                          self.employee_input, self.operation_input,
                          self.time_norm_input, self.parts_count_input]:
            input_field.setStyleSheet(input_style)
            input_field.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Левая часть формы
        left_form = QVBoxLayout()
        
        left_form.addWidget(QLabel("Шифр наряда:"))
        left_form.addWidget(self.shifr_input)
        # Создаем и настраиваем календарь как всплывающее окно
        self.calendar = QCalendarWidget(None)  # None означает отдельное окно
        self.calendar.setWindowFlags(Qt.WindowType.Popup)  # Делаем всплывающим окном
        self.calendar.setFixedSize(250, 200)  # Компактный размер
        # Настраиваем внешний вид календаря
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 8pt;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 2px;
                font-size: 8pt;
                min-width: 60px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #404040;
                border: 1px solid #5d5d5d;
            }
            QCalendarWidget QMenu {
                background-color: #2d2d2d;
                color: white;
                font-size: 8pt;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #404040;
            }
            QCalendarWidget QSpinBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                font-size: 8pt;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #1e1e1e;
                color: white;
                font-size: 8pt;
                selection-background-color: #404040;
                outline: none;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #666;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2d2d2d;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border-bottom: 1px solid #3d3d3d;
                padding: 4px;
            }
            QCalendarWidget QWidget { 
                alternate-background-color: #1e1e1e;
            }
            /* Стиль для дней недели */
            QCalendarWidget QWidget#qt_calendar_calendarview {
                border: none;
                background-color: #1e1e1e;
            }
            /* Стиль для выбранной даты */
            QCalendarWidget QTableView:item:selected {
                background-color: #404040;
                color: white;
            }
        """)
        
        # Настраиваем навигацию календаря
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        
        # Находим кнопки месяца и года
        month_button = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        year_button = self.calendar.findChild(QToolButton, "qt_calendar_yearbutton")
        
        if month_button and year_button:
            # Устанавливаем режим меню для кнопок
            month_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            year_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.calendar.clicked.connect(self.update_date_from_calendar)
        self.calendar.hide()

        # Создаем контейнер для поля даты с кнопкой
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(0)

        # Настраиваем поле даты со встроенной кнопкой
        self.date_input.setStyleSheet(input_style + """
            QLineEdit {
                padding-right: 20px;
            }
        """)
        
        # Создаем кнопку календаря как часть поля даты
        self.calendar_button = QPushButton("▼", self.date_input)
        self.calendar_button.setFixedSize(16, 16)
        self.calendar_button.clicked.connect(self.toggle_calendar)
        self.calendar_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                margin: 2px;
                padding: 0;
            }
            QPushButton:hover {
                color: #aaa;
            }
        """)
        self.calendar_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Позиционируем кнопку в правой части поля и центрируем по вертикали
        def update_button_position():
            button_y = (self.date_input.height() - self.calendar_button.height()) // 2
            self.calendar_button.move(self.date_input.width() - 18, button_y)
            
        update_button_position()
        # Обновляем позицию кнопки при изменении размера поля
        self.date_input.resizeEvent = lambda e: update_button_position()
        
        date_layout.addWidget(QLabel("Дата:"))
        date_layout.addWidget(self.date_input)
        
        left_form.addWidget(date_container)
        left_form.addWidget(QLabel("Номер цеха:"))
        left_form.addWidget(self.workshop_input)
        left_form.addWidget(QLabel("Табельный номер:"))
        left_form.addWidget(self.employee_input)
        
        # Правая часть формы
        right_form = QVBoxLayout()
        right_form.addWidget(QLabel("Код операции:"))
        right_form.addWidget(self.operation_input)
        right_form.addWidget(QLabel("Норма времени:"))
        right_form.addWidget(self.time_norm_input)
        right_form.addWidget(QLabel("Количество деталей:"))
        right_form.addWidget(self.parts_count_input)
        
        # Добавляем формы в горизонтальный layout
        form_widget_left = QWidget()
        form_widget_left.setLayout(left_form)
        form_widget_right = QWidget()
        form_widget_right.setLayout(right_form)
        
        form_layout.addWidget(form_widget_left)
        form_layout.addWidget(form_widget_right)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_record)
        self.update_button = QPushButton("Обновить")
        self.update_button.clicked.connect(self.update_record)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_record)
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)
        
        # Таблица данных
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Шифр", "Дата", "Цех", "Таб. номер", 
            "Операция", "Норма времени", "Кол-во деталей"
        ])
        self.table.cellClicked.connect(self.load_record_to_form)
        
        # Настройка равномерного распределения столбцов
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Настройка стиля и выравнивания таблицы
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2d2d2d;
                color: white;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
            QTableWidget {
                gridline-color: #3d3d3d;
                background-color: #1e1e1e;
                color: white;
                selection-background-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                text-align: center;
            }
        """)
        
        # Настройка выравнивания текста в заголовках и ячейках
        for i in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Устанавливаем выравнивание для всех ячеек в столбце
            self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Добавляем все элементы на вкладку
        form_container = QWidget()
        form_container.setLayout(form_layout)
        buttons_container = QWidget()
        buttons_container.setLayout(buttons_layout)
        
        layout.addWidget(form_container)
        layout.addWidget(buttons_container)
        layout.addWidget(self.table)
        
        data_tab.setLayout(layout)
        self.tabs.addTab(data_tab, "Данные")

    def init_analytics_tab(self):
        """Инициализация вкладки с аналитикой"""
        analytics_tab = QWidget()
        
        # Создаем scroll area с поддержкой масштабирования
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Создаем контейнер для содержимого с поддержкой масштабирования
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Контролы для выбора периода и типа анализа
        controls_layout = QHBoxLayout()
        
        # Выбор периода
        self.period_combo = QComboBox()
        self.period_combo.addItems(["День", "Месяц", "Год"])
        self.period_combo.currentTextChanged.connect(self.update_analytics)
        
        # Выбор цеха для прогноза
        self.workshop_combo = QComboBox()
        self.workshop_combo.currentTextChanged.connect(self.update_analytics)
        
        controls_layout.addWidget(QLabel("Период:"))
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(QLabel("Цех для прогноза:"))
        controls_layout.addWidget(self.workshop_combo)
        
        # Создаем и настраиваем графики
        self.orders_canvas = FigureCanvas(self.analytics.plot_orders_by_period())
        self.productivity_canvas = FigureCanvas(
            self.analytics.plot_workshop_productivity(
                datetime.now() - timedelta(days=365),
                datetime.now()
            ) or self.analytics.plot_orders_by_period()
        )
        self.complexity_canvas = FigureCanvas(
            self.analytics.plot_operation_complexity() or 
            self.analytics.plot_orders_by_period()
        )
        
        # Устанавливаем политику размера для графиков
        for canvas in [self.orders_canvas, self.productivity_canvas, self.complexity_canvas]:
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            canvas.setMinimumHeight(300)
            canvas.setMinimumWidth(400)
            canvas.figure.set_size_inches(8, 5, forward=True)
        
        self.prediction_canvas = None
        
        # Добавляем все элементы в layout
        controls_container = QWidget()
        controls_container.setLayout(controls_layout)
        controls_container.setMaximumHeight(50)
        
        layout.addWidget(controls_container)
        
        # Добавляем заголовки и графики в контейнеры
        orders_container = QWidget()
        orders_layout = QVBoxLayout(orders_container)
        orders_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        orders_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        orders_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orders_label = QLabel("ДИНАМИКА КОЛИЧЕСТВА НАРЯДОВ")
        orders_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #363636;
                border-radius: 5px;
            }
        """)
        orders_layout.addWidget(orders_label)
        orders_layout.addWidget(self.orders_canvas)
        layout.addWidget(orders_container)

        productivity_container = QWidget()
        productivity_layout = QVBoxLayout(productivity_container)
        productivity_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        productivity_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        productivity_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        productivity_label = QLabel("ЭФФЕКТИВНОСТЬ ЦЕХОВ")
        productivity_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #363636;
                border-radius: 5px;
            }
        """)
        productivity_layout.addWidget(productivity_label)
        productivity_layout.addWidget(self.productivity_canvas)
        layout.addWidget(productivity_container)

        complexity_container = QWidget()
        complexity_layout = QVBoxLayout(complexity_container)
        complexity_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        complexity_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        complexity_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        complexity_label = QLabel("АНАЛИЗ ТРУДОЕМКОСТИ ОПЕРАЦИЙ")
        complexity_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #363636;
                border-radius: 5px;
            }
        """)
        complexity_layout.addWidget(complexity_label)
        complexity_layout.addWidget(self.complexity_canvas)
        layout.addWidget(complexity_container)
        
        # Устанавливаем scroll area
        scroll.setWidget(content_widget)
        
        # Создаем layout для вкладки с поддержкой масштабирования
        tab_layout = QVBoxLayout(analytics_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(scroll)
        
        # Устанавливаем политику размера для вкладки
        analytics_tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.addTab(analytics_tab, "Аналитика")

    def load_data(self):
        """Загрузка данных в таблицу"""
        records = self.db.get_all_records()
        self.table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            for j, value in enumerate(record):
                if j == 1:  # Для столбца с датой
                    date = QDate.fromString(str(value), "yyyy-MM-dd")
                    formatted_date = date.toString("dd.MM.yyyy")
                    self.table.setItem(i, j, QTableWidgetItem(formatted_date))
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))
        
        # Обновляем список цехов в комбобоксе
        workshops = set(record[2] for record in records)
        self.workshop_combo.clear()
        self.workshop_combo.addItems([str(w) for w in sorted(workshops)])

    def toggle_calendar(self):
        """Показать/скрыть календарь"""
        if self.calendar.isHidden():
            # Позиционируем календарь справа под полем ввода
            pos = self.date_input.mapToGlobal(self.date_input.rect().bottomRight())
            # Учитываем высоту поля ввода и смещаем влево на ширину календаря
            pos.setY(pos.y() + 2)
            pos.setX(pos.x() - self.calendar.width())
            self.calendar.move(pos)
            self.calendar.show()
        else:
            self.calendar.hide()
            
    def update_date_from_calendar(self, qdate):
        """Обновить поле даты при выборе в календаре"""
        self.date_input.setText(qdate.toString("dd.MM.yyyy"))
        self.calendar.hide()
        
    def clear_form(self):
        """Очистка формы"""
        self.shifr_input.clear()
        self.date_input.setText(QDate.currentDate().toString("dd.MM.yyyy"))
        self.workshop_input.clear()
        self.employee_input.clear()
        self.operation_input.clear()
        self.time_norm_input.clear()
        self.parts_count_input.clear()

    def get_form_data(self):
        """Получение данных из формы"""
        try:
            date = QDate.fromString(self.date_input.text(), "dd.MM.yyyy")
            if not date.isValid():
                raise ValueError("Неверный формат даты")
                
            return {
                'shifr': self.shifr_input.text(),
                'date': date.toString("yyyy-MM-dd"),
                'workshop_number': int(self.workshop_input.text()),
                'employee_number': int(self.employee_input.text()),
                'operation_code': self.operation_input.text(),
                'time_norm': float(self.time_norm_input.text()),
                'parts_count': int(self.parts_count_input.text())
            }
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода данных")
            return None

    def add_record(self):
        """Добавление новой записи"""
        data = self.get_form_data()
        if not data:
            return
            
        if self.db.add_record(**data):
            self.load_data()
            self.clear_form()
            self.update_analytics()
        else:
            QMessageBox.warning(self, "Ошибка", 
                              "Запись с таким шифром уже существует")

    def update_record(self):
        """Обновление существующей записи"""
        data = self.get_form_data()
        if not data:
            return
            
        self.db.update_record(**data)
        self.load_data()
        self.clear_form()
        self.update_analytics()

    def delete_record(self):
        """Удаление записи"""
        shifr = self.shifr_input.text()
        if not shifr:
            return
            
        self.db.delete_record(shifr)
        self.load_data()
        self.clear_form()
        self.update_analytics()

    def load_record_to_form(self, row, col):
        """Загрузка записи в форму при клике на строку таблицы"""
        self.shifr_input.setText(self.table.item(row, 0).text())
        date = QDate.fromString(self.table.item(row, 1).text(), "dd.MM.yyyy")
        self.date_input.setText(date.toString("dd.MM.yyyy"))
        self.workshop_input.setText(self.table.item(row, 2).text())
        self.employee_input.setText(self.table.item(row, 3).text())
        self.operation_input.setText(self.table.item(row, 4).text())
        self.time_norm_input.setText(self.table.item(row, 5).text())
        self.parts_count_input.setText(self.table.item(row, 6).text())

    def update_analytics(self):
        """Обновление графиков"""
        window_size = self.size()
        canvas_width = window_size.width() - 100
        canvas_height = 300
        
        # Обновляем график по периодам
        period_type = self.period_combo.currentText().lower()
        if period_type == "день":
            period_type = "day"
        elif period_type == "месяц":
            period_type = "month"
        else:
            period_type = "year"
            
        # Обновляем все графики с новыми размерами
        def update_canvas(canvas, plot_func, *args):
            if canvas:
                canvas.figure.clear()
                new_figure = plot_func(*args)
                if new_figure:
                    canvas.figure = new_figure
                    canvas.figure.set_size_inches(canvas_width/100, canvas_height/100)
                    canvas.figure.tight_layout()
                    canvas.draw()
        
        # Обновляем каждый график
        update_canvas(self.orders_canvas, 
                     self.analytics.plot_orders_by_period, 
                     period_type)
        
        update_canvas(self.productivity_canvas,
                     self.analytics.plot_workshop_productivity,
                     datetime.now() - timedelta(days=365),
                     datetime.now())
        
        update_canvas(self.complexity_canvas,
                     self.analytics.plot_operation_complexity)
        
        # Обновляем прогноз если выбран цех
        workshop = self.workshop_combo.currentText()
        if workshop:
            if not self.prediction_canvas:
                # Создаем контейнер для прогноза
                prediction_container = QWidget()
                prediction_layout = QVBoxLayout(prediction_container)
                prediction_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                prediction_container.setStyleSheet("""
                    QWidget {
                        background-color: #2d2d2d;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                prediction_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                prediction_label = QLabel("ПРОГНОЗ ПРОИЗВОДИТЕЛЬНОСТИ ЦЕХА")
                prediction_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 10px;
                        background-color: #363636;
                        border-radius: 5px;
                    }
                """)
                
                # Создаем и настраиваем canvas для прогноза
                self.prediction_canvas = FigureCanvas(
                    self.analytics.predict_workshop_productivity(int(workshop))
                )
                self.prediction_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                                   QSizePolicy.Policy.Expanding)
                self.prediction_canvas.setMinimumHeight(300)
                self.prediction_canvas.setMinimumWidth(400)
                self.prediction_canvas.figure.set_size_inches(canvas_width/100, 
                                                            canvas_height/100)
                
                # Добавляем элементы в контейнер
                prediction_layout.addWidget(prediction_label)
                prediction_layout.addWidget(self.prediction_canvas)
                
                # Добавляем контейнер в основной layout
                self.tabs.widget(1).findChild(QScrollArea).widget().layout().addWidget(
                    prediction_container)
            else:
                update_canvas(self.prediction_canvas,
                            self.analytics.predict_workshop_productivity,
                            int(workshop))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
