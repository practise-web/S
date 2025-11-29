async function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.status === 200) {

            // Save Access Token
            localStorage.setItem("access_token", data.access_token);

            window.location.href = "home.html";
        } 
        else {
            alert("Invalid email or password");
        }

    } catch (err) {
        alert("Server error");
        console.log(err);
    }
}
