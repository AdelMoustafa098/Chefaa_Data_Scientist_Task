from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd


# read the data
house_df = pd.read_csv("data/regression_data.csv")
print(house_df.head(5))

# Data inspection
print(house_df.describe())
print(house_df.info())
print(house_df.columns)

'''
    we can see that column's names have white spacing which can be misleading when accessing columns, 
    we will remove these white space and rename the columns
'''

house_df.columns = house_df.columns.str.strip()

# Building the linear regression model

# Prepare the data
X = house_df[['Size', 'Bedrooms', 'Location']]
X = pd.get_dummies(X, columns=['Location'], drop_first=True)
y = house_df['Price']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Display coefficients
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)


"""
                                            Further Steps
                                        More Complex Solution
                                        
    In more complex situations, such as when dealing with larger datasets, more features, or more sophisticated models,
    more complex steps are required:
                                        
        - Data Preprocessing: Handling missing values, scaling features, encoding categorical variables, 
                              and more complex feature engineering. we may use a ColumnTransformer that standardizes 
                              numerical features such as Size and one-hot encodes categorical features such as Location.                           
        
        
        - Pipeline: Ensures consistent application of preprocessing steps and model fitting, simplifies code, 
                    and reduces the risk of data leakage. 
        
        - Cross-Validation: Provides a more reliable estimate of model performance,
                            especially with imbalanced datasets or when overfitting is a concern.
                            
        - Hyperparameter Tuning: Essential for optimizing more complex models like Random Forests, Gradient Boosting, 
                                 or Neural Networks, where numerous hyperparameters significantly impact performance.
                                Utilize RandomizedSearchCV and GridSearchCV to find the best hyperparameters, 
                                even though Linear Regression typically has few tunable parameters. 
                                This approach demonstrates how to optimize hyperparameters in more complex models.
                                     
        - Model Evaluation:  Involves additional metrics, such as R-squared, adjusted R-squared, 
                             mean absolute error (MAE), and more, to provide a comprehensive understanding of model 
                             performance. evaluates the model using cross-validation and further 
                             refines the model with hyperparameter tuning before final evaluation on the test set.
"""