import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Load the dataset
data_path = 'sensor_values_normal_live - Copy.xlsx'
df = pd.read_excel(data_path, sheet_name='Sheet1')

# Select only numeric columns for correlation
numeric_df = df.select_dtypes(include=['float64', 'int64'])

# EDA: Visualize correlations
plt.figure(figsize=(10, 6))
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Feature Correlation Heatmap')
plt.show()
# EDA: Pairplot for feature distributions and class separation
sns.pairplot(df, hue='Category', diag_kind='kde')
plt.show()

# Preprocessing
# Encode the target variable
le = LabelEncoder()
df['Category'] = le.fit_transform(df['Category'])

# Separate features and target
X = df.drop(columns=['Category'])
y = df['Category']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Model training
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
conf_matrix = confusion_matrix(y_test, y_pred)
print(conf_matrix)

# Accuracy score
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Feature importance plot
importances = model.feature_importances_
features = X.columns

plt.figure(figsize=(10, 6))
plt.barh(features, importances, color='skyblue')
plt.title('Feature Importances')
plt.xlabel('Importance')
plt.ylabel('Features')
plt.show()
import joblib

# Save the trained model to a file
model_path = 'random_forest_model.pkl'
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")
from sklearn.preprocessing import LabelEncoder
import joblib

# Encode the target variable
le = LabelEncoder()
df['Category'] = le.fit_transform(df['Category'])

# Save the label encoder
joblib.dump(le, 'label_encoder.pkl')
print("Label encoder saved successfully.")

joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved successfully.")
# Save the feature names
feature_names = list(X.columns)
joblib.dump(feature_names, 'feature_names.pkl')
print("Feature names saved successfully.")