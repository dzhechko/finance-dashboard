# Product Requirement Document (PRD)

## Project Overview

Develop a **Streamlit** application hosted on **Railway.app** that offers a comprehensive interactive dashboard for personal finance management. The application will provide user authentication, data visualization through various interactive charts, and seamless data integration from Excel files. The user interface will be primarily in Russian to cater to the target audience.

## Core Functionalities

### 0. Logging and Debugging
- please add extended logging and debugging capabilities whenever possible
- but it should be possible to turn on and turn off logging/debugging manually based on the value of variable named DEBUG = "true" or "false" 

### 1. User Authentication

- **Description:** Implement a secure authentication system allowing users to register and log in to the application.
- **Purpose:** Ensures that personal financial data is protected and accessible only to authorized users.
- **Implementation Details:**
  - Utilize the `streamlit_authenticator` library for handling authentication processes.
  - Support user registration with email verification.
  - Provide password recovery options.
- It should be possible to turn on and turn off User Authentication based on the value of the variable named AUTH = "true" or "false"

### 2. Personal Finance Dashboard

The dashboard will feature the following interactive charts:

#### a. Net Worth Over Time (Line Chart)

- **Description:** Displays the progression of the user's net worth (assets minus liabilities) over a selected time period.
- **Purpose:** Helps users visualize their overall financial growth and identify trends.
- **Interactions:**
  - Hover over data points to view exact net worth values on specific dates.
  - Option to select different time ranges (e.g., monthly, yearly).

#### b. Income vs. Expenses (Bar Chart)

- **Description:** Compares total income against total expenses for each month or year.
- **Purpose:** Enables users to assess whether they are living within their means and identify periods of surplus or deficit.
- **Interactions:**
  - Click on a bar to view detailed breakdowns of income and expenses for that period.
  - Filter data by income sources or expense categories.

#### c. Expense Breakdown by Category (Pie/Donut Chart)

- **Description:** Illustrates the proportion of expenses allocated to various categories such as housing, food, transportation, etc.
- **Purpose:** Assists users in identifying spending patterns and pinpointing areas where costs can be reduced.
- **Interactions:**
  - Click on a category slice to view specific expenses within that category.
  - Adjust category groupings for a more detailed analysis.

#### d. Budget vs. Actual Spending (Stacked Bar Chart)

- **Description:** Compares budgeted amounts to actual spending across different categories.
- **Purpose:** Helps users adhere to their budgets and highlights categories where overspending occurs.
- **Interactions:**
  - Click on a category to view discrepancies between budgeted and actual amounts.
  - Option to adjust budget allocations directly from the chart interface.

### 3. Data Integration and Management

- **Description:** Enable users to upload Excel files (`*.xlsx`) containing their financial data, which will be visualized on the dashboard.
- **Purpose:** Provides flexibility in data management and leverages existing data formats for ease of use.
- **Implementation Details:**
  - Support Excel files with the following sheets:
    - **Net Worth Table**
      - Columns: `Date (DATE)`, `Assets (DECIMAL)`, `Liabilities (DECIMAL)`
    - **Income Table**
      - Columns: `IncomeID (INTEGER)`, `Date (DATE)`, `Source (TEXT)`, `Amount (DECIMAL)`
    - **Expenses Table**
      - Columns: `ExpenseID (INTEGER)`, `Date (DATE)`, `Category (TEXT)`, `Description (TEXT)`, `Amount (DECIMAL)`
    - **Budget Table**
      - Columns: `Category (TEXT)`, `BudgetAmount (DECIMAL)`
  - Implement data validation to ensure data integrity and consistency.
  - Provide users with feedback on successful uploads and error messages for invalid data formats.

### 4. Interactive Features

- **Description:** Enhance charts with interactivity to provide deeper analytical insights.
- **Purpose:** Allows users to engage with their data dynamically, facilitating better understanding and decision-making.
- **Implementation Details:**
  - Enable dialog boxes or tooltips that appear upon interacting with chart elements (e.g., clicking a bar or hovering over a point).
  - Display relevant analytical insights within these dialogs, such as percentage changes, comparisons to previous periods, or suggestions for budget adjustments.

## Project File Structure
/
├── app.py
├── requirements.txt
├── pages/
│   ├── authentication.py
│   └── dashboard.py
├── data/
│   └── finance_data.xlsx
├── utils/
│   └── helpers.py
└── config/
    └── config.yaml


### File Descriptions

- **app.py**
  - **Purpose:** Entry point of the Streamlit application. Manages page navigation and initializes the application.
  
- **requirements.txt**
  - **Purpose:** Lists all Python dependencies required to run the application, including `streamlit`, `streamlit_authenticator`, `streamlit_mic_recorder`, and any other necessary libraries.
  
- **pages/\***
  - **authentication.py**
    - **Purpose:** Handles user registration, login, and authentication flows using `streamlit_authenticator`.
  - **dashboard.py**
    - **Purpose:** Contains the main dashboard logic, rendering all interactive charts and handling user interactions.
  
- **data/finance_data.xlsx**
  - **Purpose:** Stores the user's financial data across various sheets (Net Worth, Income, Expenses, Budget) as specified in the project requirements.
  
- **utils/helpers.py**
  - **Purpose:** Includes helper functions for data processing, validation, and any other utility operations required by the application.
  
- **config/config.yaml**
  - **Purpose:** Stores configuration settings such as authentication parameters, theme settings, and any other configurable options for the application.

## Additional Details for Developers

### Authentication Flow

- **Registration:**
  - Users input their email and create a password.
  - Implement email verification to confirm user identity.
  
- **Login:**
  - Users enter their credentials to access the dashboard.
  - Implement session management to maintain user state.

- **Security:**
  - Store passwords securely using hashing algorithms.
  - Protect against common security vulnerabilities such as SQL injection and cross-site scripting (XSS).

### Data Handling

- **Upload Mechanism:**
  - Provide a user interface for uploading Excel files.
  - Parse the uploaded file and map data to corresponding charts.
  
- **Data Validation:**
  - Ensure that all required sheets and columns are present.
  - Validate data types and formats to prevent runtime errors.
  
- **Error Handling:**
  - Display user-friendly error messages for invalid uploads.
  - Log errors for debugging purposes without exposing sensitive information to users.

### Chart Interactivity

- **Event Handling:**
  - Capture user interactions such as clicks and hovers on chart elements.
  - Trigger dynamic dialogs or tooltips that display relevant information.
  
- **Performance Optimization:**
  - Ensure that interactive features do not degrade application performance.
  - Optimize data rendering for large datasets.

### Localization

- **Language Settings:**
  - Ensure that all menu options and user-facing text are presented in Russian.
  - Maintain separate language files or configurations to manage translations effectively.
  
- **System Prompts:**
  - When interfacing with YandexGPT, ensure that prompts are in Russian.
  - For OpenAI-compatible models, use English prompts as required.

### Deployment on Railway.app

- **Configuration:**
  - Set up environment variables and configuration settings as per Railway.app requirements.
  
- **Continuous Integration:**
  - Implement CI/CD pipelines to automate testing and deployment.
  
- **Scalability:**
  - Design the application architecture to handle multiple users concurrently without performance bottlenecks.

## Key Considerations

- **Adherence to Software Design Principles:**
  - **KISS, YAGNI, DRY:** Keep the application simple, implement only necessary features, and avoid code duplication.
  - **SOLID Principles:** Ensure that each module has a single responsibility, is open for extension but closed for modification, and maintains low coupling with other modules.
  - **Modularity:** Structure the project to allow easy maintenance and scalability.

- **Security and Performance:**
  - Prioritize the protection of user data through robust authentication and secure data handling practices.
  - Optimize the application for fast load times and responsive interactions.

- **User Experience:**
  - Design intuitive and user-friendly interfaces.
  - Ensure that interactive elements provide meaningful insights and enhance data comprehension.


