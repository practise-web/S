async function signup() {
    const username = document.getElementById("signupName").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    if (!username || !email || !password) {
        alert("Please fill all fields");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/auth/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.status === 201) {
            window.location.href = "otp.html?email=" + encodeURIComponent(email);
        } 
        else {
            alert(data.message || "Signup failed");
        }

    } catch (err) {
        alert("Server error");
        console.log(err);
    }
}
