# Skill-2030 Dashboard

A powerful and interactive dashboard built with Streamlit and Plotly for analyzing branch-wise performance of students during interview sessions. This dashboard provides a comprehensive view of student performance metrics across various branches and includes visualizations such as bar charts, line charts, scatter plots, and pie charts.

## Features

- **Interactive Visualizations**: Visualize branch-wise student distribution, performance scores, and other metrics using Plotly's bar charts, line charts, scatter plots, and pie charts.
- **Performance Metrics**: Calculate and display the average performance score, number of failed students, and number of incomplete interviews for each branch.
- **Branch Performance Insights**: Identify branches that have the highest/lowest average performance scores, failure rates, and incomplete interviews.
- **Dynamic Session Filtering**: Filter and analyze the interview sessions by selecting different interview pools dynamically.
- **Streamlined Data Handling**: Leverages Pandas for data manipulation and Plotly for rendering charts, ensuring efficient performance.

## Demo

Add a link to your app deployed on Streamlit sharing platform (or a screenshot if not deployed yet).

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [Development](#development)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

To install and run the project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/varshi45/skill-2030.git
    ```
   
2. Navigate to the project directory:
    ```bash
    cd skill-2030
    ```
   
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit app:
    ```bash
    streamlit run main.py
    ```

## Usage

1. **Step 1**: After launching the app, select an interview pool from the dropdown menu to filter sessions.
2. **Step 2**: View the branch-wise distribution of students for the selected test.
3. **Step 3**: Explore different performance metrics such as average score, failure count, and incomplete sessions in the branch-wise line charts.
4. **Step 4**: Use the scatter plot to visualize the performance scores for individual sessions.
5. **Step 5**: Analyze the branch-wise performance using the interactive pie chart.

## Development

To contribute or modify the project:

1. Fork the repository.
2. Create a new feature branch:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them:
    ```bash
    git commit -m "Add your commit message"
    ```
4. Push to your branch:
    ```bash
    git push origin feature/your-feature-name
    ```
5. Create a Pull Request.

### Folder Structure

```plaintext
├── app.py                    # template logic file
├── main.py                    # Main application file
├── db_logic.py                # Contains database connection logic
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── utils/                     # Utility functions for fetching and processing data
│   ├── home.py
│   ├── interviews.py
└── ...
```

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
