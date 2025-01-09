import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class Analytics:
    def __init__(self, database):
        self.db = database
        plt.style.use('dark_background')
        self.colors = ['#00ff88', '#00bfff', '#ff3399', '#ffcc00', '#ff6600', '#9933ff']
        
        # Настройка глобального стиля для адаптивных графиков
        plt.rcParams.update({
            'figure.facecolor': '#1e1e1e',
            'axes.facecolor': '#1e1e1e',
            'savefig.facecolor': '#1e1e1e',
            'axes.grid': True,
            'grid.alpha': 0.2,
            'grid.color': '#ffffff',
            'figure.autolayout': True,
            'figure.constrained_layout.use': True,
            'figure.constrained_layout.h_pad': 0.1,
            'figure.constrained_layout.w_pad': 0.1,
            'figure.subplot.left': 0.12,
            'figure.subplot.right': 0.95,
            'figure.subplot.top': 0.95,
            'figure.subplot.bottom': 0.12,
            'figure.subplot.wspace': 0.2,
            'figure.subplot.hspace': 0.2,
            'figure.dpi': 100,
            'figure.max_open_warning': 0,
            'axes.labelpad': 8,
            'xtick.major.pad': 5,
            'ytick.major.pad': 5,
            'font.size': 10,
            'axes.titlesize': 10,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9
        })

    def plot_orders_by_period(self, period_type='month'):
        """Построение графика количества нарядов по периодам"""
        plt.close('all')  # Закрываем все предыдущие фигуры
        data = self.db.get_orders_by_period(period_type)
        periods, counts = zip(*data) if data else ([], [])
        
        # Создаем фигуру с автоматическим масштабированием
        fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)
        
        # Создаем градиент для столбцов
        colors = np.linspace(0, 1, len(periods))
        bars = plt.bar(periods, counts, color=plt.cm.Greens(colors))
        
        # Форматируем даты на оси X
        formatted_periods = []
        for period in periods:
            if len(period) == 10:  # Для дат формата YYYY-MM-DD
                date = datetime.strptime(period, '%Y-%m-%d')
                formatted_periods.append(date.strftime('%d.%m.%Y'))
            else:
                formatted_periods.append(period)
                
        plt.xticks(range(len(periods)), formatted_periods, rotation=45)
        plt.xlabel('Период', labelpad=8, color='white')
        plt.ylabel('Количество нарядов', labelpad=8, color='white')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, color='white')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        return fig

    def plot_workshop_productivity(self, start_date, end_date):
        """Построение круговой диаграммы производительности цехов"""
        data = self.db.get_workshop_productivity(start_date, end_date)
        if not data:
            return None
            
        workshops, parts, productivity = zip(*data)
        
        plt.close('all')  # Закрываем все предыдущие фигуры
        # Создаем фигуру с автоматическим масштабированием
        fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)
        
        # Создаем градиентную цветовую схему
        colors = plt.cm.Spectral(np.linspace(0, 1, len(workshops)))
        
        wedges, texts, autotexts = plt.pie(
            productivity, 
            labels=[f'Цех {w}' for w in workshops],
            autopct='%1.1f%%',
            colors=colors,
            shadow=False,
            startangle=90,
            wedgeprops=dict(width=0.7)
        )
        
        # Улучшаем внешний вид подписей
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=9)
        
        plt.axis('equal')
        return fig

    def plot_operation_complexity(self):
        """Построение гистограммы трудоемкости операций"""
        data = self.db.get_operation_complexity()
        if not data:
            return None
            
        operations, times, counts = zip(*data)
        
        plt.close('all')  # Закрываем все предыдущие фигуры
        # Создаем фигуру с автоматическим масштабированием
        fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)
        
        # Создаем градиент для столбцов
        colors = plt.cm.cool(np.linspace(0, 1, len(operations)))
        bars = plt.bar(operations, times, color=colors)
        
        # Добавляем свечение
        for bar in bars:
            bar.set_alpha(0.8)
            
        plt.xticks(rotation=45)
        plt.xlabel('Код операции', labelpad=8, color='white')
        plt.ylabel('Среднее время (норма)', labelpad=8, color='white')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9, color='white')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        return fig

    def predict_workshop_productivity(self, workshop_number):
        """Прогноз производительности цеха на следующие 2 месяца"""
        # Получаем все записи и преобразуем в DataFrame
        records = self.db.get_all_records()
        if not records:
            fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
            ax = fig.add_subplot(111)
            plt.text(0.5, 0.5, 'Нет данных для построения прогноза',
                    ha='center', va='center', color='white',
                    fontsize=10, transform=ax.transAxes)
            plt.axis('off')
            return fig
            
        df = pd.DataFrame(records, columns=['shifr', 'date', 'workshop_number', 
                                          'employee_number', 'operation_code', 
                                          'time_norm', 'parts_count'])
        
        # Фильтруем данные по цеху
        df = df[df['workshop_number'] == workshop_number].copy()
        if df.empty:
            fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
            ax = fig.add_subplot(111)
            plt.text(0.5, 0.5, f'Нет данных для цеха {workshop_number}',
                    ha='center', va='center', color='white',
                    fontsize=10, transform=ax.transAxes)
            plt.axis('off')
            return fig
            
        # Преобразуем даты и считаем производительность
        df['date'] = pd.to_datetime(df['date'])
        df['productivity'] = df['parts_count'] / df['time_norm']
        
        # Группируем по месяцам
        monthly = df.groupby(df['date'].dt.to_period('M'))['productivity'].mean()
        if len(monthly) < 3:  # нужно минимум 3 месяца для прогноза
            fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
            ax = fig.add_subplot(111)
            plt.text(0.5, 0.5, 
                    f'Для построения прогноза необходимо\n' +
                    f'минимум 3 месяца данных для цеха {workshop_number}\n' +
                    f'Текущее количество месяцев: {len(monthly)}',
                    ha='center', va='center', color='white',
                    fontsize=10, transform=ax.transAxes)
            plt.axis('off')
            return fig
            
        # Подготовка данных для регрессии
        X = np.arange(len(monthly)).reshape(-1, 1)
        y = monthly.values
        
        # Обучение модели
        model = LinearRegression()
        model.fit(X, y)
        
        # Прогноз на следующие 2 месяца
        future_months = np.array([[len(monthly)], [len(monthly) + 1]])
        predictions = model.predict(future_months)
        
        # Построение графика
        plt.close('all')  # Закрываем все предыдущие фигуры
        # Создаем фигуру с автоматическим масштабированием
        fig = plt.figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)
        
        # График фактической производительности с градиентной заливкой
        x = np.arange(len(monthly))
        plt.plot(x, monthly.values, color='#00ff88', linewidth=2, marker='o',
                label='Фактическая производительность')
        plt.fill_between(x, monthly.values, alpha=0.2, color='#00ff88')
        
        # Добавляем прогноз
        last_date = monthly.index[-1]
        future_dates = [
            last_date + pd.offsets.MonthEnd(1),
            last_date + pd.offsets.MonthEnd(2)
        ]
        plt.plot([str(last_date), str(future_dates[0]), str(future_dates[1])],
                [monthly.values[-1], predictions[0], predictions[1]], 
                color=self.colors[1], linewidth=2, linestyle='--', marker='s',
                label='Прогноз на 2 месяца')
        
        plt.xticks(range(len(monthly)), monthly.index.astype(str), rotation=45, color='white')
        plt.xlabel('Период', labelpad=8, color='white')
        plt.ylabel('Производительность\n(детали/норма времени)', 
                  labelpad=8, color='white')
        
        # Добавляем сетку и легенду
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper left', fontsize=9)
        return fig
