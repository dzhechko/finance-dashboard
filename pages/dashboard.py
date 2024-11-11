import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import logger, get_debug_status, validate_excel_file, get_auth_required
from typing import Dict, Tuple, Any, List
import numpy as np
from datetime import datetime, timedelta
import calendar

# Configure page settings with dark theme
st.set_page_config(
    page_title="Личный Финансовый Дашборд",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Set dark theme
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #262730;
        }
        
        /* Text color */
        .stMarkdown, .stText {
            color: #fafafa;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #fafafa !important;
        }
        
        /* Metric labels */
        [data-testid="stMetricLabel"] {
            color: #fafafa !important;
        }
        
        /* Metric values */
        [data-testid="stMetricValue"] {
            color: #fafafa !important;
        }
    </style>
""", unsafe_allow_html=True)

class FinanceDashboard:
    def __init__(self):
        self.debug_mode = get_debug_status()
        if 'finance_data' not in st.session_state:
            st.session_state.finance_data = None

    def load_data(self, file) -> bool:
        """Load and validate Excel data with enhanced error reporting"""
        try:
            if self.debug_mode:
                logger.debug(f"Attempting to load file: {file.name}")
            
            # Reset file pointer to beginning
            file.seek(0)
            
            if validate_excel_file(file):
                # Reset file pointer again before reading
                file.seek(0)
                
                try:
                    data = {}
                    sheets_to_load = {
                        'net_worth': "Net Worth Table",
                        'income': "Income Table",
                        'expenses': "Expenses Table",
                        'budget': "Budget Table"
                    }
                    
                    for key, sheet_name in sheets_to_load.items():
                        try:
                            df = pd.read_excel(file, sheet_name=sheet_name)
                            if self.debug_mode:
                                logger.debug(f"Loaded {sheet_name} with shape {df.shape}")
                                logger.debug(f"Columns: {df.columns.tolist()}")
                                logger.debug(f"Data types: {df.dtypes.to_dict()}")
                            data[key] = df
                        except Exception as e:
                            logger.error(f"Error loading sheet {sheet_name}: {str(e)}")
                            return False
                    
                    # Convert dates with explicit format
                    date_format = '%Y-%m-%d'  # Adjust this based on your Excel date format
                    for key in ['net_worth', 'income', 'expenses']:
                        try:
                            if isinstance(data[key]['Date'].iloc[0], str):
                                data[key]['Date'] = pd.to_datetime(data[key]['Date'], format=date_format)
                            else:
                                data[key]['Date'] = pd.to_datetime(data[key]['Date'])
                            
                            if self.debug_mode:
                                logger.debug(f"Converted dates in {key}: {data[key]['Date'].head()}")
                        except Exception as e:
                            logger.error(f"Error converting dates in {key}: {str(e)}")
                            logger.error(f"Sample date values: {data[key]['Date'].head()}")
                            return False
                    
                    st.session_state.finance_data = data
                    logger.info("Financial data loaded successfully")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error reading Excel sheets: {str(e)}")
                    return False
            else:
                if self.debug_mode:
                    logger.debug("File validation failed")
                return False
        except Exception as e:
            logger.error(f"Error loading financial data: {str(e)}")
            return False

    def get_time_filtered_data(self, data: pd.DataFrame, time_range: str) -> pd.DataFrame:
        """Filter data based on selected time range"""
        try:
            if time_range == "MAX":
                return data
                
            # Get current date
            current_date = pd.Timestamp.now()
            
            # Calculate start date based on time range
            if time_range == "1M":
                start_date = current_date - pd.DateOffset(months=1)
            elif time_range == "3M":
                start_date = current_date - pd.DateOffset(months=3)
            elif time_range == "6M":
                start_date = current_date - pd.DateOffset(months=6)
            elif time_range == "1Y":
                start_date = current_date - pd.DateOffset(years=1)
            else:
                return data
                
            # Filter data
            return data[data['Date'] >= start_date]
            
        except Exception as e:
            logger.error(f"Error filtering data by time range: {e}")
            return data

    def plot_net_worth(self) -> go.Figure:
        """Create net worth line chart with time range filter"""
        try:
            data = st.session_state.finance_data['net_worth']
            time_range = st.session_state.get('time_range', "6M")
            
            # Apply time filter
            data = self.get_time_filtered_data(data, time_range)
            
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
        """Create income vs expenses bar chart with time range filter"""
        try:
            income_data = st.session_state.finance_data['income']
            expense_data = st.session_state.finance_data['expenses']
            time_range = st.session_state.get('time_range', "6M")
            
            # Apply time filter
            income_data = self.get_time_filtered_data(income_data, time_range)
            expense_data = self.get_time_filtered_data(expense_data, time_range)
            
            # Get selected categories
            selected_categories = st.session_state.get('selected_categories', 
                                                     expense_data['Category'].unique())
            
            # Filter expenses by selected categories
            expense_data = expense_data[expense_data['Category'].isin(selected_categories)]
            
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
            
            # Store available months for analysis
            st.session_state.available_months = expenses_monthly.index.astype(str).tolist()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating income vs expenses plot: {e}")
            return None

    def show_monthly_analysis(self, selected_month: str = None) -> None:
        """Show detailed analysis for selected month"""
        try:
            income_data = st.session_state.finance_data['income']
            expense_data = st.session_state.finance_data['expenses']
            
            # Get current month and selected month
            current_month = pd.Period(datetime.now(), freq='M')
            
            if selected_month:
                try:
                    analysis_month = pd.Period(selected_month, freq='M')
                except:
                    analysis_month = current_month
            else:
                analysis_month = current_month
            
            # Calculate metrics for selected month
            month_income = income_data[
                income_data['Date'].dt.to_period('M') == analysis_month
            ]['Amount'].sum()
            
            month_expenses = expense_data[
                expense_data['Date'].dt.to_period('M') == analysis_month
            ]['Amount'].sum()
            
            savings_rate = ((month_income - month_expenses) / month_income * 100 
                           if month_income > 0 else 0)
            
            # Display analysis
            st.write(f"""
            💡 **Анализ за {analysis_month.strftime('%B %Y')}:**
            - Доходы: {month_income:,.0f} ₽
            - Расходы: {month_expenses:,.0f} ₽
            - Норма сбережений: {savings_rate:.1f}%
            """)
            
            # Show category breakdown for selected month
            month_expenses_by_category = expense_data[
                expense_data['Date'].dt.to_period('M') == analysis_month
            ].groupby('Category')['Amount'].sum().sort_values(ascending=False)
            
            st.write("**Расходы по категориям:**")
            for cat, amount in month_expenses_by_category.items():
                st.write(f"- {cat}: {amount:,.0f} ₽")
                
        except Exception as e:
            logger.error(f"Error showing monthly analysis: {e}")
            st.error("Ошибка при отображении анализа")

    def plot_expense_breakdown(self) -> go.Figure:
        """Create expense breakdown pie chart with time range filter"""
        try:
            expense_data = st.session_state.finance_data['expenses']
            time_range = st.session_state.get('time_range', "6M")
            
            # Apply time filter
            expense_data = self.get_time_filtered_data(expense_data, time_range)
            
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
        """Create budget vs actual spending chart with time range filter"""
        try:
            expense_data = st.session_state.finance_data['expenses']
            budget_data = st.session_state.finance_data['budget']
            time_range = st.session_state.get('time_range', "6M")
            
            # Apply time filter
            expense_data = self.get_time_filtered_data(expense_data, time_range)
            
            # Get selected categories
            selected_categories = st.session_state.get('selected_categories', 
                                                     expense_data['Category'].unique())
            
            # Calculate total expenses for filtered period
            total_expenses = expense_data[
                expense_data['Category'].isin(selected_categories)
            ].groupby('Category')['Amount'].sum()
            
            # Filter budget data by selected categories
            budget_data = budget_data[budget_data['Category'].isin(selected_categories)]
            
            # Create comparison DataFrame
            comparison = pd.DataFrame({
                'Category': budget_data['Category'],
                'Budget': budget_data['BudgetAmount'],
                'Actual': [total_expenses.get(cat, 0) for cat in budget_data['Category']]
            })
            
            if self.debug_mode:
                logger.debug(f"Budget comparison data:\n{comparison}")
            
            fig = go.Figure()
            
            # Add Budget bars
            fig.add_trace(go.Bar(
                x=comparison['Category'],
                y=comparison['Budget'],
                name='Бюджет',
                marker_color='#3498db'
            ))
            
            # Add Actual spending bars
            fig.add_trace(go.Bar(
                x=comparison['Category'],
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
            # Time range selector for charts
            st.subheader("Настройки отображения")
            time_range = st.select_slider(
                "Период времени",
                options=["1M", "3M", "6M", "1Y", "MAX"],
                value=st.session_state.get('time_range', "6M"),
                help="Выберите период времени для отображения данных на графиках"
            )
            
            # Update time range in session state
            if time_range != st.session_state.get('time_range'):
                st.session_state.time_range = time_range
                
            # Category filters for multiple charts
            expense_data = st.session_state.finance_data['expenses']
            categories = sorted(expense_data['Category'].unique())
            
            # Add "Select All" option
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Выбрать все"):
                    st.session_state.selected_categories = categories
            
            with col2:
                # Use session state to maintain selected categories across reruns
                if 'selected_categories' not in st.session_state:
                    st.session_state.selected_categories = categories
                    
                selected_categories = st.multiselect(
                    "Фильтр категорий расходов",
                    categories,
                    default=st.session_state.selected_categories,
                    help="Выберите категории для отображения в графиках расходов и бюджета",
                    key='category_filter'  # Add unique key
                )
            
            # Update session state only if selection changed
            if selected_categories != st.session_state.selected_categories:
                st.session_state.selected_categories = selected_categories
            
            if len(selected_categories) == 0:
                st.warning("Пожалуйста, выберите хотя бы одну категорию")
            
        except Exception as e:
            logger.error(f"Error adding chart interactions: {e}")
            st.error("Ошибка при добавлении интерактивных элементов")

def main():
    st.title("Финансовый дашборд")
    
    # Check authentication
    if not st.session_state.get('authenticated', False) and get_auth_required():
        st.warning("Пожалуйста, выполните вход в систему")
        return
    
    dashboard = FinanceDashboard()
    
    # Add sample template download
    st.markdown("""
    ### Формат данных
    Файл Excel должен содержать следующие листы:
    1. **Net Worth Table** (Чистая тоимость)
       - Date: Дата
       - Assets: Активы
       - Liabilities: Обязательства
    
    2. **Income Table** (Дооды)
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
                        
                        # Add monthly analysis with month selection
                        if st.checkbox("Показать детальный анализ"):
                            available_months = st.session_state.get('available_months', [])
                            if available_months:
                                selected_month = st.selectbox(
                                    "Выберите месяц для анализа",
                                    options=available_months,
                                    index=len(available_months)-1  # Default to latest month
                                )
                                dashboard.show_monthly_analysis(selected_month)
                            else:
                                dashboard.show_monthly_analysis()  # Show current month if no data available
                
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