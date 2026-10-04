import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    matthews_corrcoef,
)

# 1. Load the data we exported from PostgreSQL
df = pd.read_csv("data/processed/churn_features_v4.csv")

# 2. Turn customer_state (text, e.g. "SP") into numeric 0/1 columns,
#    one new column per state - this is called "one-hot encoding"
df = pd.get_dummies(df, columns=["customer_state"], drop_first=True)

# 3. Separate the "features" (what the model looks at)
#    from the "label" (what we're trying to predict)
state_columns = [c for c in df.columns if c.startswith("customer_state_")]
features = ["total_spent", "total_freight", "avg_review_score"] + state_columns

X = df[features]
y = df["churned"]

# 4. Split into a training set and a test set
#    The model learns from the training set, and we check its
#    accuracy on the test set, which it has NEVER seen.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training on {len(X_train)} customers, testing on {len(X_test)} customers")
print(f"Using {len(features)} features ({len(state_columns)} are state columns)")

# 5. Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Make predictions on the test set, and check how good they are
y_pred = model.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.2%}")

mcc = matthews_corrcoef(y_test, y_pred)
print(f"Matthews Correlation Coefficient (MCC): {mcc:.3f}")

print("\nDetailed report:")
print(classification_report(y_test, y_pred, target_names=["Not Churned", "Churned"]))

# 7. Which features actually mattered most to the model?
print("Top 10 most important features:")
importances = sorted(
    zip(features, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True,
)
for name, importance in importances[:10]:
    print(f"  {name}: {importance:.3f}")