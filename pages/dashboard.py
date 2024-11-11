import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import logger, get_debug_status, validate_excel_file
from typing import Dict, Tuple, Any, List
import numpy as np
from datetime import datetime, timedelta
import calendar

class FinanceDashboard:
    def __init__(self):
        self.debug_mode = get_debug_status()
        if 'finance_data' not in st.session_state:
            st.session_state.finance_data = None

    def load_data(self, file) -> bool:
        """Load and validate Excel data"""
        try:
            if self.debug_mode:
                logger.debug(f"Attempting to load file: {file.name}")
            
            # Reset file pointer to beginning
            file.seek(0)
            
            if validate_excel_file(file):
                # Reset file pointer again before reading
                file.seek(0)
                
                try:
                    data = {
                        'net_worth': pd.read_excel(file, sheet_name="Net Worth Table"),
                        'income': pd.read_excel(file, sheet_name="Income Table"),
                        'expenses': pd.read_excel(file, sheet_name="Expenses Table"),
                        'budget': pd.read_excel(file, sheet_name="Budget Table")
                    }
                    
                    # Convert dates
                    for key in ['net_worth', 'income', 'expenses']:
                        try:
                            data[key]['Date'] = pd.to_datetime(data[key]['Date'])
                        except Exception as e:
                            logger.error(f"Error converting dates in {key}: {e}")
                            return False
                    
                    st.session_state.finance_data = data
                    if self.debug_mode:
                        logger.debug("Financial data loaded successfully")
                        for key, df in data.items():
                            logger.debug(f"{key} shape: {df.shape}")
                    return True
                except Exception as e:
                    logger.error(f"Error reading Excel sheets: {e}")
                    return False
            else:
                if self.debug_mode:
                    logger.debug("File validation failed")
                return False
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")
            return False

    def plot_net_worth(self) -> go.Figure:
        """Create net worth line chart"""
        try:
            data = st.session_state.finance_data['net_worth']
            
            fig = go.Figure()
            
            # Add Assets line
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Assets'],
                name='Активы',
                line=dict(color='#2ecc71'),
                hovertemplate='%{y:,.2f} ₽<extra></extra>'
            ))
            
            # Add Liabilities line
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Liabilities'],
                name='Обязательства',
                line=dict(color='#e74c3c'),
                hovertemplate='%{y:,.2f} ₽<extra></extra>'
            ))
            
            # Add Net Worth line
            net_worth = data['Assets'] - data['Liabilities']
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=net_worth,
                name='Чистая стоимость',
                line=dict(color='#3498db'),
                hovertemplate='%{y:,.2f} ₽<extra></extra>'
            ))
            
            fig.update_layout(
                title='Динамика чистой стоимости активов',
                xaxis_title='Дата',
                yaxis_title='Сумма (₽)',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating net worth plot: {e}")
            return None

    def plot_income_vs_expenses(self) -> go.Figure:
        """Create income vs expenses bar chart"""
        try:
            income_data = st.session_state.finance_data['income']
            expense_data = st.session_state.finance_data['expenses']
            
            # Aggregate by month
            income_monthly = income_data.groupby(
                income_data['Date'].dt.to_period('M')
            )['Amount'].sum()
            
            expenses_monthly = expense_data.groupby(
                expense_data['Date'].dt.to_period('M')
            )['Amount'].sum()
            
            fig = go.Figure()
            
            # Add Income bars
            fig.add_trace(go.Bar(
                x=income_monthly.index.astype(str),
                y=income_monthly.values,
                name='Доходы',
                marker_color='#2ecc71'
            ))
            
            # Add Expenses bars
            fig.add_trace(go.Bar(
                x=expenses_monthly.index.astype(str),
                y=expenses_monthly.values,
                name='Расходы',
                marker_color='#e74c3c'
            ))
            
            fig.update_layout(
                title='Доходы и расходы по месяцам',
                xaxis_title='Месяц',
                yaxis_title='Сумма (₽)',
                barmode='group',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating income vs expenses plot: {e}")
            return None

    def plot_expense_breakdown(self) -> go.Figure:
        """Create expense breakdown pie chart"""
        try:
            expense_data = st.session_state.finance_data['expenses']
            
            # Aggregate by category
            category_expenses = expense_data.groupby('Category')['Amount'].sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=category_expenses.index,
                values=category_expenses.values,
                hole=.3,
                hovertemplate="%{label}<br>%{value:,.2f} ₽<br>%{percent}<extra></extra>"
            )])
            
            fig.update_layout(
                title='Структура расходов по категориям'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating expense breakdown plot: {e}")
            return None

    def plot_budget_vs_actual(self) -> go.Figure:
        """Create budget vs actual spending chart"""
        try:
            expense_data = st.session_state.finance_data['expenses']
            budget_data = st.session_state.finance_data['budget']
            
            # Get current month's expenses
            current_month = datetime.now().replace(day=1)
            monthly_expenses = expense_data[
                expense_data['Date'].dt.to_period('M') == pd.Period(current_month, freq='M')
            ]
            
            # Aggregate expenses by category
            actual_expenses = monthly_expenses.groupby('Category')['Amount'].sum()
            
            # Merge with budget data
            comparison = pd.DataFrame({
                'Budget': budget_data.set_index('Category')['BudgetAmount'],
                'Actual': actual_expenses
            }).fillna(0)
            
            fig = go.Figure()
            
            # Add Budget bars
            fig.add_trace(go.Bar(
                x=comparison.index,
                y=comparison['Budget'],
                name='Бюджет',
                marker_color='#3498db'
            ))
            
            # Add Actual spending bars
            fig.add_trace(go.Bar(
                x=comparison.index,
                y=comparison['Actual'],
                name='Фактические расходы',
                marker_color='#e74c3c'
            ))
            
            fig.update_layout(
                title='Бюджет vs. Фактические расходы',
                xaxis_title='Категория',
                yaxis_title='Сумма (₽)',
                barmode='group',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating budget vs actual plot: {e}")
            return None

    def calculate_insights(self) -> Dict[str, Any]:
        """Calculate financial insights from the data"""
        try:
            insights = {}
            
            # Net Worth Insights
            net_worth_data = st.session_state.finance_data['net_worth']
            current_net_worth = net_worth_data['Assets'].iloc[-1] - net_worth_data['Liabilities'].iloc[-1]
            prev_net_worth = net_worth_data['Assets'].iloc[-2] - net_worth_data['Liabilities'].iloc[-2]
            net_worth_change = ((current_net_worth - prev_net_worth) / prev_net_worth) * 100
            
            insights['net_worth'] = {
                'current': current_net_worth,
                'change': net_worth_change,
                'trend': 'положительный' if net_worth_change > 0 else 'отрицательный'
            }
            
            # Income vs Expenses Insights
            income_data = st.session_state.finance_data['income']
            expense_data = st.session_state.finance_data['expenses']
            
            current_month = datetime.now().replace(day=1)
            current_month_income = income_data[
                income_data['Date'].dt.to_period('M') == pd.Period(current_month, freq='M')
            ]['Amount'].sum()
            
            current_month_expenses = expense_data[
                expense_data['Date'].dt.to_period('M') == pd.Period(current_month, freq='M')
            ]['Amount'].sum()
            
            savings_rate = ((current_month_income - current_month_expenses) / current_month_income) * 100 if current_month_income > 0 else 0
            
            insights['monthly'] = {
                'income': current_month_income,
                'expenses': current_month_expenses,
                'savings_rate': savings_rate
            }
            
            # Top Expense Categories
            top_expenses = expense_data.groupby('Category')['Amount'].sum().nlargest(3)
            insights['top_expenses'] = {
                'categories': top_expenses.index.tolist(),
                'amounts': top_expenses.values.tolist()
            }
            
            # Budget Analysis
            budget_data = st.session_state.finance_data['budget']
            monthly_expenses = expense_data[
                expense_data['Date'].dt.to_period('M') == pd.Period(current_month, freq='M')
            ]
            
            over_budget_categories = []
            for _, budget_row in budget_data.iterrows():
                category = budget_row['Category']
                budget_amount = budget_row['BudgetAmount']
                actual_amount = monthly_expenses[
                    monthly_expenses['Category'] == category
                ]['Amount'].sum()
                
                if actual_amount > budget_amount:
                    over_budget_categories.append({
                        'category': category,
                        'budget': budget_amount,
                        'actual': actual_amount,
                        'overspend': actual_amount - budget_amount
                    })
            
            insights['budget_warnings'] = over_budget_categories
            
            if self.debug_mode:
                logger.debug("Financial insights calculated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error calculating insights: {e}")
            return {}

    def render_insights_sidebar(self) -> None:
        """Render financial insights in the sidebar"""
        try:
            insights = self.calculate_insights()
            
            st.sidebar.title("Финансовые показатели")
            
            # Net Worth Section
            st.sidebar.subheader("Чистая стоимость")
            col1, col2 = st.sidebar.columns(2)
            col1.metric(
                "Текущая",
                f"{insights['net_worth']['current']:,.0f} ₽",
                f"{insights['net_worth']['change']:+.1f}%"
            )
            
            # Monthly Overview
            st.sidebar.subheader("Обзор за месяц")
            col1, col2 = st.sidebar.columns(2)
            col1.metric("Доходы", f"{insights['monthly']['income']:,.0f} ₽")
            col2.metric("Расходы", f"{insights['monthly']['expenses']:,.0f} ₽")
            st.sidebar.metric("Норма сбережений", f"{insights['monthly']['savings_rate']:.1f}%")
            
            # Top Expenses
            st.sidebar.subheader("Топ расходов")
            for cat, amount in zip(
                insights['top_expenses']['categories'],
                insights['top_expenses']['amounts']
            ):
                st.sidebar.text(f"{cat}: {amount:,.0f} ₽")
            
            # Budget Warnings
            if insights['budget_warnings']:
                st.sidebar.subheader("⚠️ Превышение бюджета")
                for warning in insights['budget_warnings']:
                    with st.sidebar.expander(warning['category']):
                        st.write(f"Бюджет: {warning['budget']:,.0f} ₽")
                        st.write(f"Факт: {warning['actual']:,.0f} ₽")
                        st.write(f"Превышение: {warning['overspend']:,.0f} ₽")
            
        except Exception as e:
            logger.error(f"Error rendering insights: {e}")
            st.sidebar.error("Ошибка при отображении показателей")

    def add_chart_interactions(self) -> None:
        """Add interactive elements to the dashboard"""
        try:
            # Time range selector for Net Worth chart
            st.subheader("Настройки отображения")
            time_range = st.select_slider(
                "Период времени",
                options=["1M", "3M", "6M", "1Y", "MAX"],
                value="6M"
            )
            
            # Category filters for Expense Breakdown
            expense_data = st.session_state.finance_data['expenses']
            categories = expense_data['Category'].unique()
            selected_categories = st.multiselect(
                "Фильтр категорий расходов",
                categories,
                default=categories
            )
            
            # Update session state
            st.session_state.time_range = time_range
            st.session_state.selected_categories = selected_categories
            
        except Exception as e:
            logger.error(f"Error adding chart interactions: {e}")
            st.error("Ошибка при добавлении интерактивных элементов")

def main():
    st.title("Финансовый дашборд")
    
    dashboard = FinanceDashboard()
    
    # Add sample template download
    st.markdown("""
    ### Формат данных
    Файл Excel должен со��ержать с��едующие листы:
    1. **Net Worth Table** (Чистая стоимость)
       - Date: Дата
       - Assets: Активы
       - Liabilities: Обязательства
    
    2. **Income Table** (Доходы)
       - IncomeID: ID дохода
       - Date: Дата
       - Source: Источник
       - Amount: Сумма
    
    3. **Expenses Table** (Расходы)
       - ExpenseID: ID расхода
       - Date: Дата
       - Category: Категория
       - Description: Описание
       - Amount: Сумма
    
    4. **Budget Table** (Бюджет)
       - Category: Категория
       - BudgetAmount: Сумма бюджета
    """)
    
    # File upload section with clearer instructions
    st.markdown("### Загрузка данных")
    uploaded_file = st.file_uploader(
        "Загрузите файл Excel с финансовыми данными (.xlsx)",
        type=["xlsx"],
        help="Файл должен содержать все необходимые листы и колонки"
    )
    
    if uploaded_file is not None:
        with st.spinner("Загрузка и проверка данных..."):
        if dashboard.load_data(uploaded_file):
            # Render insights sidebar
            dashboard.render_insights_sidebar()
            
            # Add interactive features
            dashboard.add_chart_interactions()
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "Чистая стоимость",
                "Доходы и расходы",
                "Структура расходов",
                "Бюджет"
            ])
            
            with tab1:
                fig_net_worth = dashboard.plot_net_worth()
                if fig_net_worth:
                    st.plotly_chart(fig_net_worth, use_container_width=True)
                    
                    # Add explanatory text
                    with st.expander("📊 Как читать этот график"):
                        st.write("""
                        - **Активы** (зеленая линия) показывают общую стоимость всего вашего имущества
                        - **Обязательства** (красная линия) отображают ваши долги и задолженности
                        - **Чистая стоимость** (синяя линия) - это разница между активами и обязательствами
                        """)
            
            with tab2:
                fig_income_expenses = dashboard.plot_income_vs_expenses()
                if fig_income_expenses:
                    st.plotly_chart(fig_income_expenses, use_container_width=True)
                    
                    # Add monthly analysis
                    if st.checkbox("Показать детальный анализ"):
                        insights = dashboard.calculate_insights()
                        st.write(f"""
                        💡 **Анализ за текущий месяц:**
                        - Доходы: {insights['monthly']['income']:,.0f} ₽
                        - Расходы: {insights['monthly']['expenses']:,.0f} ₽
                        - Норма сбережений: {insights['monthly']['savings_rate']:.1f}%
                        """)
            
            with tab3:
                fig_expenses = dashboard.plot_expense_breakdown()
                if fig_expenses:
                    st.plotly_chart(fig_expenses, use_container_width=True)
                    
                    # Add top expenses analysis
                    insights = dashboard.calculate_insights()
                    st.write("🔍 **Топ-3 категории расходов:**")
                    for cat, amount in zip(
                        insights['top_expenses']['categories'][:3],
                        insights['top_expenses']['amounts'][:3]
                    ):
                        st.write(f"- {cat}: {amount:,.0f} ₽")
            
            with tab4:
                fig_budget = dashboard.plot_budget_vs_actual()
                if fig_budget:
                    st.plotly_chart(fig_budget, use_container_width=True)
                    
                    # Add budget warnings
                    insights = dashboard.calculate_insights()
                    if insights['budget_warnings']:
                        st.warning("⚠️ Обнаружено превышение бюджета в следующих категориях:")
                        for warning in insights['budget_warnings']:
                            st.write(f"""
                            **{warning['category']}**
                            - Превышение: {warning['overspend']:,.0f} ₽
                            """)
        else:
                st.error("""
                Ошибка при загрузке файла. Проверьте формат данных:
                - Все необходимые листы присутствуют
                - Все колонки имеют правильные названия
                - Даты в правильном формате
                - Числовые значения корректны
                """)
                st.info("Включите режим отладки в настройках для получения подробной информации об ошибке.")

if __name__ == "__main__":
    main() 