# PCCA Implementation modified from Gunderson's at https://github.com/gwgundersen/ml/blob/master/probabilistic_canonical_correlation_analysis.py

"""============================================================================
Probabilistic canonical correlation analysis. For references in comments:

    A Probabilistic Interpretation of Canonical Correlation Analysis.
    Bach, Jordan (2006).

    The EM algorithm for mixtures of factor analyzers.
    Ghahramani, Hinton (1996).
============================================================================"""

import numpy as np

inv = np.linalg.inv


# -----------------------------------------------------------------------------

class PCCA:

    def __init__(self, n_components, n_iters, regularization=1.0):
        """Initialize probabilistic CCA model.
        """
        self.k = n_components
        self.n_iters = n_iters
        self.reg = regularization

    def fit(self, X1, X2):
        """Fit model via EM.
        """
        self._init_params(X1, X2)
        #np.linalg.cholesky(self.Psi)
        print('is psd')
        for _ in range(self.n_iters):
            self._em_step()
            #np.linalg.cholesky(self.Psi)

    def transform(self, X1, X2):
        """Embed data using fitted model.
        """
        X = np.hstack([X1, X2]).T
        Psi_inv = inv(self.Psi)
        M = inv(np.eye(self.k) + self.W.T @ Psi_inv @ self.W)
        Z = M @ self.W.T @ Psi_inv @ X
        return Z.T

    def fit_transform(self, X1, X2):
        self.fit(X1, X2)
        return self.transform(X1, X2)

    def sample(self, n_samples=None):
        """Sample from the fitted model.
        """

        if n_samples is None:
          n_samples = self.n

        Psi_inv = inv(self.Psi)
        M = inv(np.eye(self.k) + self.W.T @ Psi_inv @ self.W)
        Z_post_mean = M @ self.W.T @ Psi_inv @ self.X

        X_mean = self.W @ Z_post_mean
        X_samples = np.zeros((self.n, self.p))
        for i in range(self.n):
            X_samples[i] = np.random.multivariate_normal(X_mean[:, i], self.Psi)

        # Partition the columns => (X1, X2)
        X1_samples = X_samples[:, :self.p1]  # shape => (n, p1)
        X2_samples = X_samples[:, self.p1:]  # shape => (n, p2)

        return X1_samples, X2_samples

# -----------------------------------------------------------------------------

    def _em_step(self):
        Psi_inv = inv(self.Psi)
        M = inv(np.eye(self.k) + self.W.T @ Psi_inv @ self.W)
        Z = M @ self.W.T @ Psi_inv @ self.X
        Ezz = Z @ Z.T + self.n * M

        # Update W explicitly
        W_new = (self.X @ Z.T) @ inv(Ezz)

        # Compute residuals explicitly
        X_recon = W_new @ Z
        residual = self.X - X_recon

        # Clearly separate Psi1 and Psi2
        residual1 = residual[:self.p1, :]
        residual2 = residual[self.p1:, :]

        Psi1_new = (residual1 @ residual1.T) / self.n + self.reg * np.eye(self.p1)
        Psi2_new = (residual2 @ residual2.T) / self.n + self.reg * np.eye(self.p2)

        # Combine Psi clearly
        self.Psi = np.block([
            [Psi1_new, np.zeros((self.p1, self.p2))],
            [np.zeros((self.p2, self.p1)), Psi2_new]
        ])

        # Update W
        self.W = (self.X @ Z.T) @ inv(Ezz)



    def _init_params(self, X1, X2):
        """Initialize parameters.
        """
        self.X1, self.X2 = X1, X2
        self.n, self.p1 = self.X1.shape
        _, self.p2 = self.X2.shape
        self.p = self.p1 + self.p2

        # Initialize sample covariances matrices.
        self.X = np.hstack([X1, X2]).T
        assert(self.X.shape == (self.p, self.n))
        self.Sigma1 = np.cov(self.X1.T)
        assert(self.Sigma1.shape == (self.p1, self.p1))
        self.Sigma2 = np.cov(self.X2.T)
        assert(self.Sigma2.shape == (self.p2, self.p2))

        # Initialize W.
        W1 = np.random.random((self.p1, self.k))
        W2 = np.random.random((self.p2, self.k))
        self.W = np.vstack([W1, W2])
        assert(self.W.shape == (self.p, self.k))

        # Initialize Psi.
        prior_var1 = 1
        prior_var2 = 1
        Psi1 = prior_var1 * np.eye(self.p1)
        Psi2 = prior_var2 * np.eye(self.p2)
        Psi = np.block([[Psi1, np.zeros((self.p1, self.p2))],
                        [np.zeros((self.p2, self.p1)), Psi2]])
        self.Psi = Psi