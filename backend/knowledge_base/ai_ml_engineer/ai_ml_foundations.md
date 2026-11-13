# Role: AI / Machine Learning Engineer
# Source Corpus: "Machine Learning" (Tom Mitchell) & "The Hundred-Page Machine Learning Book" (Andriy Burkov)

## Module 1: Supervised Learning Fundamentals & Loss Optimization
In supervised learning, the dataset consists of input-output pairs D = {(x_i, y_i)}. The goal is to find a function f: X -> Y that minimizes expected empirical risk over the data distribution.
For regression tasks, the Mean Squared Error (MSE) loss is defined as:
L_MSE(y, y_hat) = (1/N) * sum((y_i - y_hat_i)^2)
For binary classification, Binary Cross-Entropy (BCE) or Log Loss is:
L_BCE(y, y_hat) = -(1/N) * sum(y_i * log(y_hat_i) + (1 - y_i) * log(1 - y_hat_i))
Optimization is primarily performed using Gradient Descent:
theta := theta - alpha * grad(L(theta))
Variants include Stochastic Gradient Descent (SGD), Mini-batch Gradient Descent, and adaptive learning rate optimizers such as Adam, RMSprop, and AdaGrad. Momentum updates prevent oscillations along high-curvature ravines by maintaining an exponentially decaying moving average of past gradients.

## Module 2: Overfitting, Generalization, and Regularization
Overfitting occurs when a model learns noise and idiosyncrasies in the training set rather than the underlying data-generating distribution, resulting in low training error but high generalization error.
The Bias-Variance Tradeoff decomposes the expected test error into three components:
Expected Test Error = Bias^2 + Variance + Irreducible Error
- High Bias (Underfitting): The model makes strong simplifying assumptions (e.g., linear model for non-linear data).
- High Variance (Overfitting): The model is overly sensitive to fluctuations in the training data.
Regularization techniques penalize model complexity:
- L2 Regularization (Ridge / Weight Decay): Adds sum(w_j^2) to the loss function. Drives weights smoothly towards zero without forcing sparsity, mitigating multicollinearity.
- L1 Regularization (Lasso): Adds sum(|w_j|) to the loss function. Produces sparse weight vectors, acting as embedded feature selection.
- ElasticNet: Convex combination of L1 and L2 penalties.
- Dropout: Randomly deactivates a fraction p of neurons during each forward-backward training pass in deep neural networks to prevent co-adaptation.
- Early Stopping: Halts training when validation loss ceases to decrease across a predefined patience threshold.

## Module 3: Decision Trees, Random Forests, and Ensemble Learning
Decision trees partition the input space hierarchically based on purity metrics:
- Shannon Entropy: H(S) = -sum(p_i * log2(p_i))
- Information Gain: IG(S, A) = H(S) - sum((|S_v| / |S|) * H(S_v)) (used in ID3 and C4.5)
- Gini Impurity: Gini(S) = 1 - sum(p_i^2) (used in CART)
To combat single-tree variance, ensemble learning techniques combine multiple weak learners:
- Bagging (Bootstrap Aggregation): Trains independent models on bootstrap samples with replacement and averages their predictions. Random Forests introduce feature subsampling (sqrt(p) features per split) to decorrelate individual trees.
- Boosting: Sequentially trains models where each subsequent learner focuses on the residual errors of the previous ensemble.
  - AdaBoost adjusts instance sample weights.
  - Gradient Boosted Decision Trees (GBDT), XGBoost, LightGBM, and CatBoost minimize arbitrary differentiable loss functions via gradient descent in function space, utilizing second-order Taylor approximations and histogram-based binning.

## Module 4: Neural Networks, Backpropagation, and Deep Learning
Feedforward neural networks compute layer-wise transformations:
h^(l) = sigma(W^(l) * h^(l-1) + b^(l))
Non-linear activation functions:
- Sigmoid: sigma(z) = 1 / (1 + exp(-z)), susceptible to vanishing gradients when |z| is large.
- ReLU (Rectified Linear Unit): f(z) = max(0, z), computationally efficient and alleviates vanishing gradients, though subject to the "dying ReLU" problem. Leaky ReLU and GELU address dead zones.
Backpropagation computes partial derivatives of the loss with respect to all network parameters via the chain rule of calculus:
dL/dW^(l) = dL/dh^(l) * dh^(l)/dz^(l) * dz^(l)/dW^(l)
Vanishing and Exploding Gradients are mitigated via:
- Normalized weight initializations (He initialization for ReLU, Xavier/Glorot for Sigmoid/Tanh)
- Batch Normalization and Layer Normalization
- Residual skip connections (ResNet): h^(l) = F(h^(l-1)) + h^(l-1)

## Module 5: Retrieval-Augmented Generation (RAG) & Embeddings
Retrieval-Augmented Generation couples an external factual knowledge retriever with a generative LLM:
1. Ingestion: Documents are segmented into chunks with sliding-window overlap to preserve semantic continuity across split boundaries.
2. Embedding Generation: Dense representations are computed using semantic encoders (e.g., all-MiniLM, text-embedding-3-small, BGE). Cosine similarity measures closeness:
similarity(u, v) = (u . v) / (||u|| * ||v||)
3. Vector Retrieval: Approximate Nearest Neighbor (ANN) search using HNSW (Hierarchical Navigable Small World) or IVF-PQ graphs.
4. Grounded Prompting: The top-k relevant chunks are dynamically injected into the system prompt with strict citation constraints to ground the model and eliminate hallucination.
