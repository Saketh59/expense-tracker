document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("auth-form");
    const formTitle = document.getElementById("form-title");
    const toggleText = document.getElementById("toggle-text");
    const toggleLink = document.getElementById("toggle-link");
    const usernameField = document.getElementById("username-field");
    const message = document.getElementById("message");

    let isLogin = true;

    if (toggleLink) {
        toggleLink.addEventListener("click", (e) => {
            e.preventDefault();
            isLogin = !isLogin;
            formTitle.textContent = isLogin ? "Login" : "Signup";
            toggleText.innerHTML = isLogin
                ? `Don't have an account? <a href="#" id="toggle-link">Sign up</a>`
                : `Already have an account? <a href="#" id="toggle-link">Login</a>`;
            
            usernameField.style.display = isLogin ? "none" : "block";
            form.querySelector("button").textContent = isLogin ? "Login" : "Signup";

            // Reattach event listener for the new toggle link
            document.getElementById("toggle-link").addEventListener("click", (e) => {
                e.preventDefault();
                toggleLink.click();
            });
        });
    }

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const username = isLogin ? null : document.getElementById("username").value;

            const endpoint = isLogin ? "/login" : "/signup";
            const data = isLogin ? { email, password } : { username, email, password };

            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (response.ok) {
                if (isLogin) {
                    window.location.href = "/dashboard"; // Redirect to dashboard
                } else {
                    message.textContent = "Signup successful! You can now log in.";
                    isLogin = true;
                    formTitle.textContent = "Login";
                    toggleText.innerHTML = `Don't have an account? <a href="#" id="toggle-link">Sign up</a>`;
                    usernameField.style.display = "none";
                    form.querySelector("button").textContent = "Login";

                    document.getElementById("toggle-link").addEventListener("click", (e) => {
                        e.preventDefault();
                        toggleLink.click();
                    });
                }
            } else {
                message.textContent = result.error;
            }
        });
    }

    // Handling Transactions & Uploads
    const transactionForm = document.getElementById("transaction-form");
    const csvUploadForm = document.getElementById("csv-upload-form");
    const receiptUploadForm = document.getElementById("receipt-upload-form");
    const budgetAdvice = document.getElementById("budget-advice");
    const transactionsDiv = document.getElementById("transactions");

    if (transactionForm) {
        transactionForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(transactionForm);

            const response = await fetch("/add_transaction", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            alert(result.message);
            loadTransactions();
        });
    }

    if (csvUploadForm) {
        csvUploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(csvUploadForm);

            const response = await fetch("/upload_csv", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            alert(result.message);
            loadTransactions();
        });
    }

    if (receiptUploadForm) {
        receiptUploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(receiptUploadForm);

            const response = await fetch("/upload_receipt", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            alert(result.message);
            loadTransactions();
        });
    }

    async function loadTransactions() {
        if (!transactionsDiv) return;
        const response = await fetch("/get_transactions");
        const data = await response.json();

        transactionsDiv.innerHTML = "";
        data.transactions.forEach((txn) => {
            const txnDiv = document.createElement("div");
            txnDiv.classList.add("transaction-entry");
            txnDiv.innerHTML = `<strong>${txn.category}</strong>: ${txn.amount} (${txn.mode}) - ${txn.date}`;
            transactionsDiv.appendChild(txnDiv);
        });

        if (budgetAdvice) {
            budgetAdvice.textContent = data.budget_advice;
        }
    }

    // Load transactions on page load
    if (transactionsDiv) loadTransactions();
});
document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.getElementById('auth-form');
    const toggleLink = document.getElementById('toggle-link');
    const formTitle = document.getElementById('form-title');
    const usernameField = document.getElementById('username');
    const message = document.getElementById('message');
    
    let isLogin = true;

    // Toggle between login and signup forms
    toggleLink.addEventListener('click', function(e) {
        e.preventDefault();
        isLogin = !isLogin;
        
        if (isLogin) {
            formTitle.textContent = 'Login';
            toggleLink.textContent = 'Sign up';
            usernameField.style.display = 'none';
            authForm.querySelector('button').textContent = 'Login';
        } else {
            formTitle.textContent = 'Sign Up';
            toggleLink.textContent = 'Login';
            usernameField.style.display = 'block';
            authForm.querySelector('button').textContent = 'Sign Up';
        }
    });

    // Handle form submission
    authForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // In a real app, you would validate credentials here
        // For this example, we'll just redirect to dashboard
        window.location.href = 'dashboard.html';
    });
});