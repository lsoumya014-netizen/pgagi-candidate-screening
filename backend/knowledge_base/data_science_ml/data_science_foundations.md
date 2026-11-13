# Role: Data Science / Applied ML Engineer
# Source Corpus: "Introduction to Machine Learning with Python" (Müller & Guido) & "Master Machine Learning Algorithms" (Jason Brownlee)

## Module 1: Exploratory Data Analysis, Imputation, & Feature Engineering
Real-world datasets contain missing values, skewed distributions, categorical features, and noisy outliers.
- Missing Data Handling:
  - Missing Completely at Random (MCAR), Missing at Random (MAR), and Missing Not at Random (MNAR).
  - Imputation strategies: Median/Mode imputation for univariate pipelines; KNN Imputer and Iterative Imputer (MICE) for multivariate relationships.
- Categorical Encoding:
  - One-Hot Encoding for low-cardinality nominal variables.
  - Target/Mean Encoding for high-cardinality variables (requires smoothing and out-of-fold calculation to prevent severe data leakage).
  - Ordinal Encoding for ranked attributes.
- Feature Scaling:
  - StandardScaler (Z-score normalization): (x - mu) / sigma. Critical for distance-based algorithms (KNN, SVM, K-Means) and gradient-based models.
  - RobustScaler: Uses median and IQR to scale in the presence of extreme outliers.
  - MinMaxScaler: Scales values into [0, 1] range.

## Module 2: Dimensionality Reduction & Unsupervised Learning
High-dimensional feature spaces suffer from the "Curse of Dimensionality", leading to data sparsity and computational inefficiency.
- Principal Component Analysis (PCA):
  - Linear orthogonal transformation that projects data onto directions of maximum variance (eigenvectors of the empirical covariance matrix).
  - Eigenvalue decomposition or Singular Value Decomposition (SVD): X = U * Sigma * V^T.
  - Scree plots and cumulative explained variance ratio guide the selection of components.
- t-SNE & UMAP:
  - Non-linear manifold learning techniques primarily employed for 2D/3D visual exploration and cluster discovery.
- Clustering:
  - K-Means: Partitioning algorithm minimizing within-cluster sum of squares (inertia). Evaluated via Silhouette Score and Davies-Bouldin index.
  - DBSCAN: Density-based spatial clustering that identifies arbitrary cluster geometries and labels sparse noise points.

## Module 3: Validation Strategies & Avoiding Data Leakage
Rigorous validation prevents optimistic performance estimates and deployment failures:
- K-Fold Cross Validation & Stratified K-Fold: Maintains class balance across splits for imbalanced datasets.
- Time-Series Split: Preserves chronological order (walk-forward validation) to prevent look-ahead bias.
- Data Leakage Prevention:
  - Preprocessing parameters (mean, standard deviation, imputation medians, encoding mappings) must be computed ONLY on training folds and subsequently applied to test folds.
  - Using scikit-learn `Pipeline` or `ColumnTransformer` guarantees atomic encapsulation of fit and transform steps.

## Module 4: Comprehensive Model Evaluation Metrics
Accuracy is misleading on imbalanced datasets:
- Confusion Matrix: True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN).
- Precision = TP / (TP + FP) (crucial when false alarms are costly, e.g., spam detection).
- Recall / Sensitivity = TP / (TP + FN) (crucial when misses are fatal, e.g., fraud or medical diagnosis).
- F1-Score = 2 * (Precision * Recall) / (Precision + Recall) (harmonic mean).
- ROC Curve & PR Curve:
  - ROC-AUC measures ranking ability across classification thresholds; PR-AUC is superior when positive class prevalence is rare (<5%).
- Log-Loss / Cross-Entropy: Penalizes confident misclassifications.
